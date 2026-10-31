# 1. Creezi index.html, articol.html, despre.html și stil.css pentru blogul tău
#    (exemplu: așa începe index.html)
#    <!DOCTYPE html>
#    <html lang="ro">
#    <head>
#      <meta charset="utf-8">
#      <title>Blogul meu</title>
#      <link rel="stylesheet" href="stil.css">
#    </head>
#    În despre.html pui și: <img src="https://..." alt="..."> și o listă <ol><li>...</li></ol>


# 2. În stil.css: un tag, o clasă, article p, un :hover; articolele au chenar și padding
#    scrii așa: article { border: 1px solid #ccc; padding: 1em; }
#               a:hover { color: darkred; }


# 3. Pornești serverul cu comanda din lecție; în terminal, toate cererile trebuie să aibă 200
#    scrii așa: python -m http.server 8000 --bind 0.0.0.0 --directory capitole/44-html-css


# 4. Aici, în html_css.py: pagina_lista(articole) întoarce HTML-ul complet, cu escape() pe texte;
#    scrii rezultatul în generat.html
#    scrii așa: from html import escape
#               def pagina_lista(articole):
#                   randuri = [f"<li>{escape(a['titlu'])}</li>" for a in articole]
#    apoi:      Path(...).write_text(html, encoding="utf-8")


# 5. Un articol cu titlul <b>Test</b> & alte „ghilimele”, care trebuie să apară exact așa
#    scrii așa: {"titlu": "<b>Test</b> & alte „ghilimele”", "data": "...", "categorie": "..."}
