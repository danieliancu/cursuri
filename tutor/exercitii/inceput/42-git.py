# 1. Configurezi git și creezi repository-ul, în terminal (exemplu: așa arată comenzile)
#    git config --global user.name "Ana Popescu"
#    git config --global user.email "ana@exemplu.ro"
#    git init
#    git config core.fileMode false


# 2. Creezi fișierul .gitignore în rădăcina proiectului; verifici cu git status --short
#    scrii așa (în .gitignore): __pycache__/
#                               .venv/
#                               .env
#                               .pytest_cache/


# 3. Primul commit cu tot proiectul
#    scrii așa: git add .
#               git commit -m "Adaugă proiectul inițial"


# 4. Aici, în git.py, funcția salut(nume); apoi commit
#    scrii așa: def salut(nume):
#                   return f"Salut, {nume}!"


# 5. Ramura majuscule: .title() pe nume, commit, înapoi pe main, git merge
#    scrii așa: git switch -c majuscule
#               git switch main
#               git merge majuscule


# 6. Un conflict provocat: același rând schimbat pe două ramuri, rezolvat în editor, apoi commit
#    scrii așa: git merge alta-ramura   (apoi ștergi <<<<<<<, ======= și >>>>>>>)


# 7. Verifici: cel puțin 5 commit-uri, cu mesaje clare, la prezent
#    scrii așa: git log --oneline
