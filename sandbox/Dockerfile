# Mediul izolat în care rulează codul fiecărui elev (un container per elev).
# La o schimbare aici, crește versiunea imaginii (PYTUTOR_SANDBOX_IMAGE în settings.py):
# containerele elevilor create din imaginea veche se refac automat (vezi sandbox.ensure).
FROM python:3.12-slim

# git pentru lecția 42; ramura implicită „main”, ca în lecție și pe GitHub.
# Proiectele sunt montate din Windows cu alt proprietar decât `student`: fără safe.directory, git le refuză.
# (Tot din cauza montajului, fișierele par executabile; `git init` își scrie singur core.fileMode în repository,
# deci setarea se face local, după init — lecția 42 o arată.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system init.defaultBranch main \
    && git config --system --add safe.directory '*'

# Django (lecțiile 45+), black/ruff/mypy (lecția 40), pytest (lecția 41), Django REST Framework (lecția 60),
# gunicorn și whitenoise (lecția 61).
RUN useradd --create-home --uid 1000 student \
    && python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir "Django>=5.2,<6" "black>=24,<26" "ruff>=0.6,<1" "mypy>=1.11,<2" \
       "pytest>=8,<9" "djangorestframework>=3.15,<4" "gunicorn>=23,<24" "whitenoise>=6.7,<7" \
    && chown -R student:student /opt/venv

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

USER student
WORKDIR /work

# PID 1 doar ține containerul în viață; comenzile elevului rulează prin `docker exec`.
CMD ["tail", "-f", "/dev/null"]
