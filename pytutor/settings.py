"""Setări PyTutor — aplicație locală, un singur utilizator."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Încarcă variabilele din .env (dacă există) fără dependențe externe."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-pytutor-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*"] if DEBUG else ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "tutor",  # primul, ca șabloanele lui de admin (base_site) să le înlocuiască pe cele implicite
    "django.contrib.admin",
    "django.contrib.humanize",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pytutor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tutor.context_processors.pytutor",
            ]
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "login"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 de zile

WSGI_APPLICATION = "pytutor.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "ro"
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
X_FRAME_OPTIONS = "SAMEORIGIN"

# --- PyTutor ---
# Proiectele elevului sunt foldere reale pe disc, ca într-un editor normal.
WORKSPACE_ROOT = Path(os.environ.get("PYTUTOR_WORKSPACES", BASE_DIR / "workspaces")).resolve()
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

# Furnizorul AI: "anthropic" (Claude) sau "openai".
PYTUTOR_PROVIDER = os.environ.get("PYTUTOR_PROVIDER", "anthropic").strip().lower()
ANTHROPIC_MODEL = os.environ.get("PYTUTOR_MODEL", "claude-opus-5-5")
ANTHROPIC_EFFORT = os.environ.get("PYTUTOR_EFFORT", "medium")
OPENAI_MODEL = os.environ.get("PYTUTOR_OPENAI_MODEL", "gpt-4.1")
# Model mic și ieftin pentru verificarea progresului (bifele din sumar), când tutorele uită să-l salveze.
OPENAI_CHECK_MODEL = os.environ.get("PYTUTOR_OPENAI_CHECK_MODEL", "gpt-4.1-mini")
ANTHROPIC_CHECK_MODEL = os.environ.get("PYTUTOR_CHECK_MODEL", "claude-haiku-5-5")

# Elevii își pot face singuri cont? (0 = doar administratorul creează conturi, din /admin/)
PYTUTOR_ALLOW_SIGNUP = os.environ.get("PYTUTOR_ALLOW_SIGNUP", "1") == "1"

# Unde rulează comenzile din terminal: "docker" (container izolat per elev) sau "local".
PYTUTOR_SANDBOX = os.environ.get("PYTUTOR_SANDBOX", "local").strip().lower()
PYTUTOR_SANDBOX_IMAGE = os.environ.get("PYTUTOR_SANDBOX_IMAGE", "pytutor-sandbox:2")
PYTUTOR_SANDBOX_MEMORY = os.environ.get("PYTUTOR_SANDBOX_MEMORY", "512m")
PYTUTOR_SANDBOX_CPUS = os.environ.get("PYTUTOR_SANDBOX_CPUS", "1")
# "bridge" = are internet (pip install) și port pentru runserver; "none" = complet izolat.
PYTUTOR_SANDBOX_NETWORK = os.environ.get("PYTUTOR_SANDBOX_NETWORK", "bridge")
# Serverul Django al elevului cu id N e publicat pe portul PORT_BASE + N.
PYTUTOR_SANDBOX_PORT_BASE = int(os.environ.get("PYTUTOR_SANDBOX_PORT_BASE", "9000"))
