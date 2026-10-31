from decimal import Decimal

from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    """Ce știe AI-ul despre un elev."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_profile")
    level = models.CharField("nivel", max_length=40, blank=True, default="")
    summary = models.TextField("despre elev", blank=True, default="")
    goals = models.TextField("obiective", blank=True, default="")
    strengths = models.TextField("puncte forte", blank=True, default="")
    weaknesses = models.TextField("de lucrat", blank=True, default="")
    # [{"topic": "list comprehensions", "status": "învățat" | "în lucru" | "de învățat"}]
    topics = models.JSONField("subiecte", default=list, blank=True)
    # Ultima lecție deschisă de elev (oricare, și una deja învățată): sumarul, editorul și tutorele pornesc de aici.
    current_topic = models.ForeignKey("Topic", on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="+", verbose_name="lecția deschisă")
    updated_at = models.DateTimeField("actualizat", auto_now=True)

    class Meta:
        verbose_name = "profil elev"
        verbose_name_plural = "profiluri elevi"

    def __str__(self):
        return f"{self.user} — {self.level or 'nivel necunoscut'}"

    @classmethod
    def for_user(cls, user) -> "StudentProfile":
        obj, _ = cls.objects.get_or_create(user=user)
        return obj

    def is_empty(self) -> bool:
        return not (self.level or self.summary or self.topics)

    def as_dict(self) -> dict:
        return {
            "level": self.level,
            "summary": self.summary,
            "goals": self.goals,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "topics": self.topics,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


STATUS_TODO, STATUS_DOING, STATUS_DONE = "de învățat", "în lucru", "învățat"
STATUS_CHOICES = [(s, s) for s in (STATUS_TODO, STATUS_DOING, STATUS_DONE)]

# `Topic.lesson_model` pentru lecțiile scrise în proiect (`tutor/lessons/`): AI-ul nu le suprascrie niciodată.
LESSON_MANUAL = "manual"


class Module(models.Model):
    """Un capitol din curriculum (ex. „Funcții”, „Django: modele”)."""

    slug = models.SlugField(unique=True)
    title = models.CharField("titlu", max_length=120)
    description = models.TextField("descriere", blank=True, default="")
    order = models.PositiveIntegerField("ordine", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "modul"
        verbose_name_plural = "module"

    def __str__(self):
        return self.title


class Topic(models.Model):
    """Un subiect din curriculum.

    Lecția vine din `tutor/lessons/NN-slug.md` (comanda `load_lessons`); doar subiectele fără fișier
    primesc o lecție scrisă de AI la prima deschidere.
    """

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="topics")
    slug = models.SlugField(unique=True)
    title = models.CharField("titlu", max_length=160)
    summary = models.TextField("ce acoperă", help_text="Folosit ca plan când AI-ul scrie lecția.")
    order = models.PositiveIntegerField("ordine", default=0)
    lesson = models.TextField("lecția (Markdown)", blank=True, default="", help_text="Lecțiile din tutor/lessons/ au prioritate; gol = AI-ul o scrie la prima deschidere.")
    lesson_model = models.CharField("scrisă de", max_length=80, blank=True, default="")
    lesson_updated_at = models.DateTimeField("lecție actualizată", null=True, blank=True)

    class Meta:
        ordering = ["module__order", "order"]
        verbose_name = "subiect"
        verbose_name_plural = "subiecte"

    def __str__(self):
        return f"{self.module.title} › {self.title}"


class TopicProgress(models.Model):
    """Statusul curent al unui elev pe un subiect."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_progress")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField("status", max_length=20, choices=STATUS_CHOICES, default=STATUS_DOING)
    updated_at = models.DateTimeField("actualizat", auto_now=True)

    class Meta:
        verbose_name = "progres pe subiect"
        verbose_name_plural = "progres pe subiecte"
        constraints = [models.UniqueConstraint(fields=["user", "topic"], name="unique_progress_per_topic")]


class TopicEvidence(models.Model):
    """O dovadă de lucru: ce a scris elevul (copie a codului) și ce a spus tutorele despre asta."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_evidence")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="evidence")
    status = models.CharField("status", max_length=20, choices=STATUS_CHOICES)
    comment = models.TextField("ce a spus tutorele")
    project = models.CharField("proiect", max_length=60, blank=True, default="")
    path = models.CharField("fișier", max_length=300, blank=True, default="")
    start_line = models.PositiveIntegerField(null=True, blank=True)
    code = models.TextField("codul elevului (copie)", blank=True, default="")
    created_at = models.DateTimeField("data", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "dovadă de lucru"
        verbose_name_plural = "dovezi de lucru"


class ExerciseAttempt(models.Model):
    """Încercările unui elev la exercițiul fix al unei lecții (tutor/exercitii/): pentru treptele de indiciu."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exercise_attempts")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="attempts")
    failed = models.PositiveIntegerField("încercări greșite", default=0)
    hints_shown = models.PositiveIntegerField("indicii văzute", default=0)
    solved_at = models.DateTimeField("rezolvat", null=True, blank=True)
    # codul de la ultima verificare: dacă următorul e cu totul altul, treptele de indiciu o iau de la capăt
    last_code = models.TextField("ultimul cod verificat", blank=True, default="")
    # „Nu lucrez la exercițiul lecției”: fișierul capitolului e verificat de tutore (sarcina lui), nu de teste
    skipped = models.BooleanField("lucrează la altceva", default=False)
    # testul care a picat ultima dată: la un test nou, primul indiciu e cel al testului (`indiciu` în TOML)
    last_test = models.CharField("ultimul test picat", max_length=200, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "încercare la exercițiu"
        verbose_name_plural = "încercări la exerciții"
        constraints = [models.UniqueConstraint(fields=["user", "topic"], name="unique_attempt_per_topic")]


class Conversation(models.Model):
    """O conversație per (elev, proiect)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_conversations")
    project = models.CharField("proiect", max_length=60)
    created_at = models.DateTimeField("creată", auto_now_add=True)
    # La conversații lungi, mesajele vechi (id <= summary_upto) nu se mai trimit la AI, ci doar rezumatul lor.
    summary = models.TextField("rezumatul mesajelor vechi", blank=True, default="")
    summary_upto = models.BigIntegerField("rezumat până la mesajul", default=0)

    class Meta:
        verbose_name = "conversație"
        verbose_name_plural = "conversații"
        constraints = [models.UniqueConstraint(fields=["user", "project"], name="unique_conversation_per_project")]

    def __str__(self):
        return f"{self.user} / {self.project}"


class CodeAnnotation(models.Model):
    """Baloanele de explicații puse de tutore pe un fișier (înlocuite la fiecare apel nou)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="code_annotations")
    project = models.CharField("proiect", max_length=60)
    path = models.CharField("fișier", max_length=300)
    # [{"line": 12, "end_line": 14, "title": "...", "text": "markdown"}]
    notes = models.JSONField("explicații", default=list)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "explicații în cod"
        verbose_name_plural = "explicații în cod"
        constraints = [models.UniqueConstraint(fields=["user", "project", "path"], name="unique_annotation_per_file")]


class ModelPrice(models.Model):
    """Prețul unui model, în USD per 1 milion de tokeni (cum facturează furnizorii).

    Potrivirea se face după prefix: „gpt-4.1” acoperă și „gpt-4.1-2025-04-14”.
    """

    model = models.CharField("model", max_length=80, unique=True)
    input_usd = models.DecimalField("input $/1M", max_digits=10, decimal_places=4)
    output_usd = models.DecimalField("output $/1M", max_digits=10, decimal_places=4)
    cache_read_usd = models.DecimalField("cache citit $/1M", max_digits=10, decimal_places=4, default=0)
    cache_write_usd = models.DecimalField("cache scris $/1M", max_digits=10, decimal_places=4, default=0)

    class Meta:
        verbose_name = "preț model"
        verbose_name_plural = "prețuri modele"
        ordering = ["model"]

    def __str__(self):
        return self.model


class CostSettings(models.Model):
    """Setări pentru afișarea costurilor (un singur rând)."""

    usd_to_gbp = models.DecimalField("curs 1 USD = ? GBP", max_digits=8, decimal_places=4, default=Decimal("0.75"))

    class Meta:
        verbose_name = "setări cost"
        verbose_name_plural = "setări cost"

    def __str__(self):
        return f"1 USD = {self.usd_to_gbp} GBP"

    @classmethod
    def get(cls) -> "CostSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class UsageRecord(models.Model):
    """Un apel la API-ul AI: tokeni consumați și costul calculat la momentul apelului."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_usage")
    project = models.CharField("proiect", max_length=60, blank=True, default="")
    provider = models.CharField("furnizor", max_length=20)
    model = models.CharField("model", max_length=80)
    input_tokens = models.PositiveIntegerField("input", default=0)
    output_tokens = models.PositiveIntegerField("output", default=0)
    cache_read_tokens = models.PositiveIntegerField("cache citit", default=0)
    cache_write_tokens = models.PositiveIntegerField("cache scris", default=0)
    cost_usd = models.DecimalField("cost USD", max_digits=12, decimal_places=6, default=0)
    priced = models.BooleanField("preț cunoscut", default=True)
    created_at = models.DateTimeField("data", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "apel AI"
        verbose_name_plural = "apeluri AI"
        ordering = ["-created_at"]


class ChatMessage(models.Model):
    """Un mesaj din istoricul trimis la AI (append-only).

    `content` păstrează blocurile exact cum vin de la API (inclusiv thinking și
    tool_use), ca să le putem retrimite neschimbate. `ui_text` e textul afișat
    pentru mesajele elevului (fără contextul tehnic atașat).
    """

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10)  # "user" | "assistant"
    content = models.JSONField()
    ui_text = models.TextField(blank=True, default="")
    is_tool_result = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "mesaj"
        verbose_name_plural = "mesaje"


class TopicCode(models.Model):
    """Codul unui elev pentru un capitol (subiect) — copie în baza de date a folderului capitolului.

    Fiecare capitol are folderul lui în proiect (`capitole/NN-slug/`), ca exercițiile simple și cele
    avansate să nu se amestece. Copia de aici permite refacerea folderului dacă dispare de pe disc.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topic_code")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="code")
    project = models.CharField("proiect", max_length=120)
    path = models.CharField("fișier", max_length=500)  # relativ la proiect
    content = models.TextField("cod", blank=True, default="")
    updated_at = models.DateTimeField("actualizat", auto_now=True)

    class Meta:
        verbose_name = "cod pe capitol"
        verbose_name_plural = "cod pe capitole"
        ordering = ["topic__module__order", "topic__order", "path"]
        constraints = [models.UniqueConstraint(fields=["user", "project", "path"], name="unique_topic_code_file")]
