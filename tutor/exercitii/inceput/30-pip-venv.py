# 1. În terminal, verifică în ce mediu rulezi (exemplu: așa se scrie)
#    python -c "import sys; print(sys.executable)"
#    python -m pip --version


# 2. În terminal: pachetele instalate și detaliile lui Django (versiunea, rândul Requires)
#    scrii așa: pip list
#               pip show django


# 3. Instalează rich și afișează aici, cu un tabel, cheltuielile pe categorii
#    scrii așa: python -m pip install rich
#               from rich.table import Table
#               tabel = Table(title="Cheltuieli pe categorii")


# 4. În rădăcina proiectului: requirements.txt scris de mână și .gitignore cu .venv/ și __pycache__/
#    scrii așa: django
#               rich


# 5. La începutul fișierului: testul pentru mediul virtual
#    scrii așa: import sys
#               if sys.prefix != sys.base_prefix:
