"""Verifică proiectul de referință al lecțiilor Django: tutor/lessons/_blog/45 … 61.

Pentru fiecare etapă (starea proiectului după lecția NN), într-o copie temporară, în containerul sandbox:
`check`, `makemigrations --check`, `migrate`, încărcarea datelor de test (_blog/date/), `test`, câteva pagini
cerute cu vezi_pagina.py (status așteptat) și, la 61, `check --deploy` cu setări de producție și `collectstatic`.
Afișează și ce fișiere s-au schimbat față de etapa anterioară — adică ce trebuie să arate lecția.

Folosire: python tools/verifica_blog.py [NN ...]      (fără argumente: toate etapele)
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifica_lectie import IGNORE, IMAGE, LESSONS, hook_dir, same_file  # noqa: E402

BLOG = LESSONS / "_blog"
PRIMA, ULTIMA = 45, 61

# Ce date de test se potrivesc cu modelele fiecărei etape (vezi _blog/README.md).
DATE = {**dict.fromkeys(range(50, 53), 50), **dict.fromkeys(range(53, 57), 53), **dict.fromkeys(range(57, 62), 57)}

PROD_ENV = {
    "DJANGO_DEBUG": "0",
    "DJANGO_SECRET_KEY": "o-cheie-lunga-si-aleatoare-doar-pentru-verificare-7f3c9a1e5b2d8046",
    "DJANGO_ALLOWED_HOSTS": "blogul-anei.ro",
}


def pagini(nr: int) -> list[tuple[str, str]]:
    """(argumentele pentru vezi_pagina.py, statusul așteptat) pentru etapa `nr`."""
    if nr < 47:
        return []
    out = [("/", "200"), ("/articol/1/", "200"), ("/articol/999/", "404")]
    if nr >= 48:
        out.append(("/despre/", "200"))
    if nr >= 55:
        out.append(("/contact/", "200"))
        out.append(("POST /contact/ nume=Mihai email=mihai@exemplu.ro 'mesaj=Salut, Ana!'", "302"))
    if nr == 56:
        out.append(("/articol/nou/", "200"))
    if nr >= 56:
        out.append(("POST /articol/2/comentariu/ autor=Mihai text=Bravo!", "302"))
    if nr >= 57:
        out += [("/articol/nou/", "302"), ("--user ana /articol/nou/", "200"),
                ("--user mihai /articol/1/editeaza/", "403"), ("/conturi/login/", "200"),
                ("/conturi/inregistrare/", "200")]
    if nr >= 58:
        out.append(("--user ana /articol/1/sterge/", "200"))
    if nr >= 60:
        out.append(("/api/articole/", "200"))
    return out


def docker(folder: Path, script: str, env: dict | None = None) -> tuple[int, str]:
    args = ["docker", "run", "--rm", "--network", "none", "-v", f"{folder}:/w", "-v", f"{hook_dir()}:/h:ro",
            "-v", f"{LESSONS}:/lectii:ro", "-w", "/w"]
    for k, v in (env or {}).items():
        args += ["-e", f"{k}={v}"]
    res = subprocess.run(args + [IMAGE, "sh", "-c", script], capture_output=True, timeout=600)
    return res.returncode, (res.stdout + res.stderr).decode("utf-8", "replace")


def check(nr: int) -> bool:
    folder = BLOG / str(nr)
    with tempfile.TemporaryDirectory(prefix=f"blog-{nr}-") as tmp:
        work = Path(tmp) / "p"
        shutil.copytree(folder, work, ignore=IGNORE)
        pasi = [
            "python manage.py check",
            "python manage.py makemigrations --check --dry-run",
            "python manage.py migrate -v 0",
        ]
        if nr in DATE:
            pasi.append(f"python manage.py loaddata /lectii/_blog/date/{DATE[nr]}.json -v 0")
        pasi.append("python manage.py test -v 1")
        for args, status in pagini(nr):  # args sunt deja scrise ca pentru shell
            vezi = f"python /h/vezi_pagina.py {args} 2>/dev/null"
            pasi.append(f"{{ {vezi} | head -1 | grep -q '^{status} ' || "
                        f"{{ echo \"pagina {args}: aștepta {status}, a primit:\"; {vezi} | head -3; exit 1; }}; }}")
        code, out = docker(work, " && ".join(pasi))
        if code == 0 and nr == ULTIMA:
            code, out2 = docker(work, "python manage.py check --deploy --fail-level WARNING && "
                                      "python manage.py collectstatic --noinput -v 0", PROD_ENV)
            out += out2
        if code:
            print(f"{nr}: EȘEC\n{out.strip()}")
            return False
        teste = next((line for line in out.splitlines() if line.startswith("Ran ")), "Ran 0 tests")
        print(f"{nr}: OK — {teste}, {len(pagini(nr))} pagini verificate")
        return True


def diff(nr: int) -> list[str]:
    """Ce s-a schimbat față de etapa anterioară (lecția 45 pornește de la un folder gol)."""
    with tempfile.TemporaryDirectory() as tmp:
        new = shutil.copytree(BLOG / str(nr), Path(tmp) / "n", ignore=IGNORE)
        files = lambda root: {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        have = files(new)
        if nr == PRIMA:
            return [f"  + {f}" for f in sorted(have)]
        old = shutil.copytree(BLOG / str(nr - 1), Path(tmp) / "o", ignore=IGNORE)
        before = files(old)
        out = [f"  + {f}" for f in sorted(have - before)]
        out += [f"  ~ {f}" for f in sorted(have & before) if not same_file(new / f, old / f)]
        out += [f"  - {f}" for f in sorted(before - have)]
        return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    etape = [int(a) for a in sys.argv[1:]] or list(range(PRIMA, ULTIMA + 1))
    ok = True
    for nr in etape:
        ok &= check(nr)
        print("\n".join(diff(nr)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
