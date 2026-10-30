import json
from functools import wraps

from django import forms
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import Http404, HttpResponseNotAllowed, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from . import ai, chapters, runner, sandbox, workspace
from .models import (
    STATUS_DOING,
    STATUS_TODO,
    CodeAnnotation,
    Conversation,
    Module,
    StudentProfile,
    Topic,
    TopicEvidence,
    TopicProgress,
)


def api(methods):
    """JSON API: cere login, verifică metoda, parsează corpul și transformă WorkspaceError în 400."""

    def deco(fn):
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Trebuie să fii autentificat.", "login": True}, status=401)
            if request.method not in methods:
                return HttpResponseNotAllowed(methods)
            body = {}
            if request.method in ("POST", "PUT") and request.body:
                try:
                    body = json.loads(request.body)
                except json.JSONDecodeError:
                    return JsonResponse({"error": "JSON invalid"}, status=400)
            try:
                result = fn(request, body, *args, **kwargs)
            except workspace.WorkspaceError as e:
                return JsonResponse({"error": str(e)}, status=400)
            return result if not isinstance(result, dict) else JsonResponse(result)

        return wrapper

    return deco


# --- Pagini ---

@ensure_csrf_cookie
@login_required
def index(request):
    return render(request, "tutor/index.html")


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label="Prenume", max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        fields = ("username", "first_name")


def signup(request):
    if not settings.PYTUTOR_ALLOW_SIGNUP:
        raise Http404("Înregistrarea e dezactivată. Cere un cont administratorului.")
    if request.user.is_authenticated:
        return redirect("index")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")
    return render(request, "registration/signup.html", {"form": form})


# --- Utilizator ---

@api(["GET"])
def me(request, body):
    u = request.user
    return {
        "username": u.get_username(),
        "name": u.first_name or u.get_username(),
        "is_staff": u.is_staff,
        "sandbox": {
            "mode": "docker" if sandbox.enabled() else "local",
            "server_url": sandbox.server_url(u) if sandbox.enabled() else "http://127.0.0.1:8001",
        },
    }


# --- Proiecte & fișiere ---

@api(["GET", "POST"])
def projects(request, body):
    if request.method == "POST":
        workspace.create_project(request.user, body.get("name", ""))
    return {"projects": workspace.list_projects(request.user)}


@api(["GET"])
def tree(request, body, project):
    return {"tree": workspace.tree(request.user, project)}


@api(["GET", "PUT", "POST", "DELETE"])
def file(request, body, project):
    u = request.user
    if request.method == "GET":
        return workspace.read_file(u, project, request.GET.get("path", ""))
    if request.method == "PUT":
        rel = workspace.write_file(u, project, body.get("path", ""), body.get("content", ""))
        chapters.sync(u, project, rel)
        return {"path": rel}
    if request.method == "POST":
        rel = workspace.create(u, project, body.get("path", ""), body.get("type", "file"))
        chapters.sync(u, project, rel)
        return {"path": rel}
    rel = request.GET.get("path", "")
    workspace.delete(u, project, rel)
    chapters.forget(u, project, rel)
    return {"ok": True}


@api(["POST"])
def rename(request, body, project):
    rel = workspace.rename(request.user, project, body.get("from", ""), body.get("to", ""))
    chapters.forget(request.user, project, body.get("from", ""))
    chapters.sync(request.user, project, rel)
    return {"path": rel}


# --- Terminal ---

@api(["POST"])
def term_run(request, body, project):
    runner.run(request.user, project, body.get("command", ""))
    return {"ok": True}


@api(["POST"])
def term_stop(request, body, project):
    runner.stop(request.user, project)
    return {"ok": True}


@api(["POST"])
def term_input(request, body, project):
    runner.send_input(request.user, project, body.get("text", ""))
    return {"ok": True}


@api(["POST"])
def term_clear(request, body, project):
    runner.clear(request.user, project)
    return {"ok": True}


@api(["GET"])
def term_output(request, body, project):
    workspace.project_dir(request.user, project)
    try:
        since = int(request.GET.get("since", "0"))
    except ValueError:
        since = 0
    return runner.output(request.user, project, since)


# --- Chat ---

@api(["GET", "POST", "DELETE"])
def chat(request, body, project):
    user = request.user
    workspace.project_dir(user, project)
    if request.method == "GET":
        return {"messages": ai.ui_messages(user, project)}
    if request.method == "DELETE":
        Conversation.objects.filter(user=user, project=project).delete()
        return {"ok": True}

    text = (body.get("message") or "").strip()
    if not text:
        return JsonResponse({"error": "Mesaj gol"}, status=400)
    ctx = body.get("context") or {}

    def sse():
        try:
            for ev in ai.chat_stream(user, project, text, ctx):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as e:  # noqa: BLE001 — orice eroare ajunge în UI, nu în gol
            yield f"data: {json.dumps({'type': 'error', 'message': f'Eroare internă: {e}'}, ensure_ascii=False)}\n\n"

    resp = StreamingHttpResponse(sse(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp


@api(["POST"])
def chapter(request, body, project):
    """Elevul a ales o lecție: îi dăm folderul de cod al capitolului și o facem lecția activă."""
    user = request.user
    topic = Topic.objects.filter(slug=body.get("topic", "")).first()
    if not topic:
        return JsonResponse({"error": "Subiect inexistent"}, status=404)
    path = chapters.ensure(user, project, topic)
    tp, created = TopicProgress.objects.get_or_create(user=user, topic=topic, defaults={"status": STATUS_DOING})
    if not created:
        if tp.status == STATUS_TODO:
            tp.status = STATUS_DOING
        tp.save()  # actualizează data, ca să devină lecția activă (și pentru tutore)
    return {"path": path, "status": tp.status}


@api(["GET", "DELETE"])
def notes(request, body, project):
    """Baloanele de explicații ale tutorelui pentru proiect: {path: [note, ...]}."""
    user = request.user
    workspace.project_dir(user, project)
    qs = CodeAnnotation.objects.filter(user=user, project=project)
    if request.method == "DELETE":
        qs.filter(path=request.GET.get("path", "")).delete()
        return {"ok": True}
    return {"notes": {a.path: a.notes for a in qs}}


@api(["GET", "DELETE"])
def profile(request, body):
    p = StudentProfile.for_user(request.user)
    if request.method == "DELETE":
        # Resetare completă: tutorele va reevalua elevul de la zero.
        p.delete()
        TopicProgress.objects.filter(user=request.user).delete()
        TopicEvidence.objects.filter(user=request.user).delete()
        p = StudentProfile.for_user(request.user)
    return {"profile": p.as_dict()}


# --- Progres & lecții ---

@ensure_csrf_cookie
@login_required
def progress_page(request):
    return render(request, "tutor/progress.html")


@api(["GET"])
def progress(request, body):
    user = request.user
    statuses, touched = {}, {}
    for tid, st, at in TopicProgress.objects.filter(user=user).values_list("topic_id", "status", "updated_at"):
        statuses[tid], touched[tid] = st, at
    counts = dict(
        TopicEvidence.objects.filter(user=user).values("topic_id").annotate(n=Count("id")).values_list("topic_id", "n")
    )
    project = request.GET.get("project", "")
    code_paths = {}
    if project:
        active = TopicProgress.objects.filter(user=user, status=STATUS_DOING).select_related("topic").order_by("-updated_at").first()
        if active:
            code_paths[active.topic_id] = chapters.ensure(user, project, active.topic)
        code_paths = {**chapters.paths_by_topic(user, project), **code_paths}
    modules = []
    for m in Module.objects.prefetch_related("topics"):
        topics = [
            {
                "slug": t.slug,
                "title": t.title,
                "summary": t.summary,
                "status": statuses.get(t.id, STATUS_TODO),
                "evidence": counts.get(t.id, 0),
                "updated_at": touched[t.id].isoformat() if t.id in touched else None,
                "code_path": code_paths.get(t.id),
            }
            for t in m.topics.all()
        ]
        modules.append({"slug": m.slug, "title": m.title, "description": m.description, "topics": topics})
    return {"profile": StudentProfile.for_user(user).as_dict(), "modules": modules}


@api(["GET"])
def topic_detail(request, body, slug):
    t = Topic.objects.select_related("module").filter(slug=slug).first()
    if not t:
        return JsonResponse({"error": "Subiect inexistent"}, status=404)
    tp = TopicProgress.objects.filter(user=request.user, topic=t).first()
    evidence = [
        {
            "status": e.status,
            "comment": e.comment,
            "project": e.project,
            "path": e.path,
            "start_line": e.start_line,
            "code": e.code,
            "created_at": e.created_at.isoformat(),
        }
        for e in TopicEvidence.objects.filter(user=request.user, topic=t)
    ]
    return {
        "slug": t.slug,
        "title": t.title,
        "module": t.module.title,
        "summary": t.summary,
        "lesson": t.lesson,
        "status": tp.status if tp else STATUS_TODO,
        "evidence": evidence,
    }


@api(["POST"])
def topic_lesson(request, body, slug):
    """Scrie lecția cu AI-ul (streaming), dacă încă nu există."""
    t = Topic.objects.select_related("module").filter(slug=slug).first()
    if not t:
        return JsonResponse({"error": "Subiect inexistent"}, status=404)
    user = request.user

    def sse():
        if t.lesson:
            yield f"data: {json.dumps({'type': 'text', 'text': t.lesson}, ensure_ascii=False)}\n\n"
            yield 'data: {"type": "done"}\n\n'
            return
        try:
            for ev in ai.generate_lesson(user, t):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as e:  # noqa: BLE001
            yield f"data: {json.dumps({'type': 'error', 'message': f'Eroare internă: {e}'}, ensure_ascii=False)}\n\n"

    resp = StreamingHttpResponse(sse(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp
