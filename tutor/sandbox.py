"""Containere Docker per elev: codul fiecăruia rulează izolat, cu limite de resurse.

Fiecare elev are un container de lungă durată (`pytutor-u<id>`) cu folderul lui de
proiecte montat în /work. Comenzile din terminal rulează în el prin `docker exec`,
deci pachetele instalate cu pip rămân până la recrearea containerului.
"""
import subprocess
from pathlib import Path

from django.conf import settings

from . import workspace

SANDBOX_DIR = Path(settings.BASE_DIR) / "sandbox"
CONTAINER_PORT = 8000  # portul pe care elevul pornește runserver în container


def enabled() -> bool:
    return settings.PYTUTOR_SANDBOX == "docker"


def container_name(user) -> str:
    return f"pytutor-u{user.pk}"


def host_port(user) -> int:
    return settings.PYTUTOR_SANDBOX_PORT_BASE + user.pk


def server_url(user) -> str:
    return f"http://localhost:{host_port(user)}"


def _quiet(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _image_exists() -> bool:
    return _quiet(["docker", "image", "inspect", settings.PYTUTOR_SANDBOX_IMAGE]).returncode == 0


def ensure(user, stream) -> None:
    """Se asigură că imaginea și containerul elevului există și rulează.

    `stream(args, intro)` rulează o comandă lungă afișându-i output-ul în terminal
    și întoarce codul de ieșire (vezi runner).
    """
    if _quiet(["docker", "version", "--format", "{{.Server.Version}}"]).returncode != 0:
        raise RuntimeError("Docker nu rulează. Pornește Docker Desktop și încearcă din nou.")

    if not _image_exists():
        rc = stream(
            ["docker", "build", "-t", settings.PYTUTOR_SANDBOX_IMAGE, str(SANDBOX_DIR)],
            "[pregătesc mediul Python izolat — prima dată durează 1-2 minute]\n",
        )
        if rc != 0:
            raise RuntimeError("Construirea imaginii sandbox a eșuat.")

    name = container_name(user)
    # Container creat dintr-o imagine mai veche (altă versiune sau aceeași etichetă reconstruită):
    # îl refacem; pachetele instalate de elev cu pip se pierd.
    current = _quiet(["docker", "image", "inspect", "-f", "{{.Id}}", settings.PYTUTOR_SANDBOX_IMAGE]).stdout.strip()
    used = _quiet(["docker", "inspect", "-f", "{{.Image}}", name])
    if used.returncode == 0 and used.stdout.strip() != current:
        remove(user)
    state = _quiet(["docker", "inspect", "-f", "{{.State.Running}}", name])
    if state.returncode != 0:
        mount = workspace.user_root(user).resolve()
        args = [
            "docker", "run", "-d",
            "--name", name,
            "--hostname", "pytutor",
            "--label", "pytutor=1",
            "--memory", settings.PYTUTOR_SANDBOX_MEMORY,
            "--cpus", settings.PYTUTOR_SANDBOX_CPUS,
            "--pids-limit", "256",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--network", settings.PYTUTOR_SANDBOX_NETWORK,
            "-v", f"{mount}:/work",
        ]
        if settings.PYTUTOR_SANDBOX_NETWORK != "none":
            args += ["-p", f"127.0.0.1:{host_port(user)}:{CONTAINER_PORT}"]
        res = _quiet(args + [settings.PYTUTOR_SANDBOX_IMAGE])
        if res.returncode != 0:
            raise RuntimeError(f"Nu pot porni containerul: {res.stderr.strip()}")
    elif state.stdout.strip() != "true":
        res = _quiet(["docker", "start", name])
        if res.returncode != 0:
            raise RuntimeError(f"Nu pot porni containerul: {res.stderr.strip()}")


def exec_args(user, project: str, command: str) -> list[str]:
    return ["docker", "exec", "-i", "-w", f"/work/{project}", container_name(user), "sh", "-c", command]


def kill_all(user) -> None:
    """Oprește tot ce rulează în containerul elevului (PID 1 e protejat de kernel)."""
    _quiet(["docker", "exec", container_name(user), "sh", "-c", "kill -9 -1"])


def remove(user) -> None:
    _quiet(["docker", "rm", "-f", container_name(user)])
