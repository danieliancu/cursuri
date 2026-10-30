"""Ce vede browserul la o adresă din proiectul Django din folderul curent (doar pentru verificarea lecțiilor).

Rulează în sandbox, din folderul proiectului, prin directiva `<!-- comanda: python /h/vezi_pagina.py ... -->`:

    vezi_pagina.py /articol/1/                       GET, afișează statusul și textul vizibil al paginii
    vezi_pagina.py --html /                          tot HTML-ul, nu doar textul
    vezi_pagina.py POST /articol/1/comentariu/ autor=Mihai "text=Bravo!"
    vezi_pagina.py --user ana /articole/nou/         cererea vine de la utilizatorul `ana` (fără parolă)
    vezi_pagina.py --follow POST /login/ ...         urmează redirecționările

Răspunsurile JSON (lecția 60) sunt afișate indentat.
"""
import json
import os
import sys
from html.parser import HTMLParser

BLOCK = {
    "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol", "br", "tr", "table", "article", "header",
    "footer", "section", "nav", "main", "form", "label", "title", "button", "textarea", "select", "dt", "dd", "hr",
}
SKIP = {"script", "style", "head"}


class Text(HTMLParser):
    """Textul vizibil, pe rânduri, ca într-un browser fără stiluri; câmpurile de formular apar ca [câmp: nume]."""

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag in BLOCK:
            self.parts.append("\n")
        if tag in ("td", "th"):
            self.parts.append("\t")  # coloanele unui tabel: separate cu „ | ” în text()
        a = dict(attrs)
        if tag == "input" and a.get("type") not in ("hidden", "submit"):
            self.parts.append(f"[câmp: {a.get('name', '?')}]")
        elif tag == "input" and a.get("type") == "submit":
            self.parts.append(f"[{a.get('value', 'Trimite')}]")
        elif tag in ("textarea", "select"):
            self.parts.append(f"[câmp: {a.get('name', '?')}]")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip -= 1
        if tag in BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        # rândurile noi din sursa HTML sunt doar spații pentru browser; rândurile vizibile vin din tag-urile bloc
        if not self.skip:
            self.parts.append(data.replace("\n", " "))

    def text(self) -> str:
        def clean(line: str) -> str:
            cells = (" ".join(cell.split()) for cell in line.split("\t"))
            return " | ".join(cell for cell in cells if cell)

        lines = (clean(line) for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)


def main() -> None:
    args = sys.argv[1:]
    show_html = "--html" in args
    follow = "--follow" in args
    user = None
    if "--user" in args:
        i = args.index("--user")
        user = args[i + 1]
        del args[i:i + 2]
    args = [a for a in args if a not in ("--html", "--follow")]
    method = args.pop(0) if args[0] in ("GET", "POST") else "GET"
    path = args.pop(0)
    data = dict(a.split("=", 1) for a in args)

    sys.path.insert(0, os.getcwd())
    settings_dirs = [d for d in os.listdir() if os.path.isfile(os.path.join(d, "settings.py"))]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{settings_dirs[0]}.settings")
    import django

    django.setup()
    from django.test import Client
    from django.test.utils import setup_test_environment

    setup_test_environment()  # permite gazda „testserver” a clientului de test
    client = Client()
    if user:
        from django.contrib.auth import get_user_model

        client.force_login(get_user_model().objects.get(username=user))
    if method == "POST":
        r = client.post(path, data, follow=follow)
    else:
        r = client.get(path, data, follow=follow)

    print(r.status_code, r.reason_phrase)
    if r.has_header("Location"):
        print("Location:", r["Location"])
    body = r.content.decode("utf-8")
    if r.get("Content-Type", "").startswith("application/json"):
        print(json.dumps(json.loads(body), ensure_ascii=False, indent=2))
    elif show_html:
        print(body.strip())
    else:
        parser = Text()
        parser.feed(body)
        print(parser.text())


if __name__ == "__main__":
    main()
