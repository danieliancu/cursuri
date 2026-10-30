"""Terminal: rulează câte o comandă per (elev, proiect) și ține output-ul în memorie.

Cu PYTUTOR_SANDBOX=docker comenzile rulează în containerul elevului; altfel direct
pe calculator (doar pentru dezvoltare locală). Suportă și procese de lungă durată
(ex. `python manage.py runserver`), care pot fi oprite din interfață.
"""
import os
import re
import shlex
import subprocess
import sys
import threading
import time

from . import sandbox, workspace

MAX_BUFFER = 300_000  # caractere păstrate per sesiune

# Mod local: `python`, `pip` și `django-admin` folosesc interpretorul aplicației (care are Django).
_PY = f'"{sys.executable}"'
_REWRITES = [
    (re.compile(r"^\s*(?:python3?|py)(?=\s|$)"), _PY),
    (re.compile(r"^\s*pip3?(?=\s|$)"), _PY + " -m pip"),
    (re.compile(r"^\s*django-admin(?=\s|$)"), _PY + " -m django"),
]


def _rewrite(cmd: str) -> str:
    for rx, prefix in _REWRITES:
        m = rx.match(cmd)
        if m:
            return prefix + cmd[m.end():]
    return cmd


class Session:
    def __init__(self):
        self.lock = threading.Lock()
        self.text = ""
        self.base = 0  # offset absolut al primului caracter din `text`
        self.proc: subprocess.Popen | None = None
        self.busy = False  # True de la pornire (inclusiv pregătirea containerului) până la final
        self.command = ""
        self.returncode: int | None = None
        self.started_at = 0.0

    @property
    def end(self) -> int:
        return self.base + len(self.text)

    def append(self, s: str) -> None:
        with self.lock:
            self.text += s
            if len(self.text) > MAX_BUFFER:
                cut = len(self.text) - MAX_BUFFER
                self.text = self.text[cut:]
                self.base += cut

    def running(self) -> bool:
        return self.busy


_sessions: dict[tuple[int, str], Session] = {}
_sessions_lock = threading.Lock()


def get(user, project: str) -> Session:
    with _sessions_lock:
        return _sessions.setdefault((user.pk, project), Session())


def _user_busy(user) -> bool:
    with _sessions_lock:
        return any(s.busy for (uid, _), s in _sessions.items() if uid == user.pk)


def _env() -> dict:
    env = os.environ.copy()
    env.update({"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    for secret in ("DJANGO_SETTINGS_MODULE", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "DJANGO_SECRET_KEY"):
        env.pop(secret, None)  # să nu ajungă în codul elevului
    return env


def _spawn(sess: Session, args, shell: bool, cwd=None, stdin=True) -> int:
    """Pornește un proces, îi copiază output-ul în sesiune și întoarce codul de ieșire."""
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    proc = subprocess.Popen(
        args,
        cwd=cwd,
        shell=shell,
        stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=_env(),
        creationflags=flags,
        start_new_session=os.name != "nt",
    )
    sess.proc = proc
    assert proc.stdout is not None
    while True:
        chunk = proc.stdout.read1(4096) if hasattr(proc.stdout, "read1") else proc.stdout.read(4096)
        if not chunk:
            break
        sess.append(chunk.decode("utf-8", errors="replace").replace("\r\n", "\n"))
    return proc.wait()


def _job(sess: Session, user, project: str, command: str) -> None:
    rc = -1
    try:
        if sandbox.enabled():
            def stream(args, intro):
                sess.append(intro)
                return _spawn(sess, args, shell=False, stdin=False)

            sandbox.ensure(user, stream)
            rc = _spawn(sess, sandbox.exec_args(user, project, command), shell=False)
        else:
            rc = _spawn(sess, _rewrite(command), shell=True, cwd=workspace.project_dir(user, project))
    except Exception as e:  # noqa: BLE001 — orice problemă ajunge în terminal
        sess.append(f"[eroare: {e}]\n")
    finally:
        sess.returncode = rc
        sess.busy = False
        sess.append(f"\n[proces terminat cu codul {rc} după {time.time() - sess.started_at:.1f}s]\n")


def run(user, project: str, command: str) -> None:
    workspace.project_dir(user, project)
    sess = get(user, project)
    command = command.strip()
    if not command:
        raise workspace.WorkspaceError("Comandă goală.")
    if sess.busy or (sandbox.enabled() and _user_busy(user)):
        raise workspace.WorkspaceError("Rulează deja o comandă. Oprește-o mai întâi.")
    sess.busy = True
    sess.append(f"\n$ {command}\n")
    sess.command = command
    sess.returncode = None
    sess.started_at = time.time()
    threading.Thread(target=_job, args=(sess, user, project, command), daemon=True).start()


def send_input(user, project: str, text: str) -> None:
    sess = get(user, project)
    proc = sess.proc
    if not sess.busy or proc is None or proc.stdin is None or proc.poll() is not None:
        raise workspace.WorkspaceError("Nu rulează niciun proces care să primească input.")
    sess.append(text + "\n")
    proc.stdin.write((text + "\n").encode("utf-8"))
    proc.stdin.flush()


def stop(user, project: str) -> None:
    sess = get(user, project)
    if not sess.busy:
        return
    sess.append("\n[oprire cerută de utilizator]\n")
    if sandbox.enabled():
        sandbox.kill_all(user)
    proc = sess.proc
    if proc is not None and proc.poll() is None:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        else:
            import signal

            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def clear(user, project: str) -> None:
    sess = get(user, project)
    with sess.lock:
        sess.base = sess.end
        sess.text = ""


def output(user, project: str, since: int = 0) -> dict:
    sess = get(user, project)
    with sess.lock:
        start = max(since, sess.base)
        return {
            "text": sess.text[start - sess.base:],
            "next": sess.end,
            "reset": since < sess.base,
            "running": sess.busy,
            "command": sess.command,
            "returncode": sess.returncode,
        }


def run_capture(user, project: str, path: str, stdin_text: str = "", timeout: int = 20) -> tuple[int | None, str]:
    """Rulează `python <path>` separat de terminalul elevului (pentru verificarea făcută de tutore).

    Întoarce (cod de ieșire sau None la timeout, output). Folosește același mediu ca terminalul:
    containerul elevului sau, în mod local, interpretorul aplicației.
    """
    workspace.safe_path(user, project, path)  # validează calea
    if sandbox.enabled():
        sandbox.ensure(user, lambda args, intro: subprocess.run(args, capture_output=True).returncode)
        args = sandbox.exec_args(user, project, f"timeout {timeout} python {shlex.quote(path)}")
        cwd, shell = None, False
    else:
        args = f"{_PY} {subprocess.list2cmdline([path])}"
        cwd, shell = workspace.project_dir(user, project), True
    try:
        res = subprocess.run(
            args, cwd=cwd, shell=shell, input=(stdin_text or "").encode("utf-8"),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=_env(), timeout=timeout + 5,
        )
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", errors="replace")
        return None, out + f"\n[oprit după {timeout}s — programul așteaptă input sau rulează la nesfârșit]"
    rc = None if (sandbox.enabled() and res.returncode == 124) else res.returncode
    out = res.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")
    if rc is None:
        out += f"\n[oprit după {timeout}s — programul așteaptă input sau rulează la nesfârșit]"
    return rc, out[-8000:]


def last_run(user, project: str) -> dict | None:
    """Rezumatul ultimei comenzi din terminalul elevului, pentru contextul tutorelui."""
    sess = get(user, project)
    if not sess.command:
        return None
    with sess.lock:
        out = sess.text[-3000:]
    return {
        "command": sess.command,
        "running": sess.busy,
        "returncode": sess.returncode,
        "started_at": sess.started_at,
        "output": out,
    }


def tail(user, project: str, chars: int = 6000) -> str:
    sess = get(user, project)
    with sess.lock:
        return sess.text[-chars:]
