from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

P = "api/projects/<str:project>/"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("progres/", views.progress_page, name="progress"),
    path("api/me", views.me),
    path("api/progress", views.progress),
    path("api/topics/<slug:slug>", views.topic_detail),
    path("api/topics/<slug:slug>/lesson", views.topic_lesson),
    path("api/projects", views.projects),
    path("api/profile", views.profile),
    path(P + "tree", views.tree),
    path(P + "file", views.file),
    path(P + "rename", views.rename),
    path(P + "chat", views.chat),
    path(P + "notes", views.notes),
    path(P + "chapter", views.chapter),
    path(P + "exercitiu/verifica", views.exercise_check),
    path(P + "exercitiu/sari", views.exercise_skip),
    path(P + "pas", views.step),
    path(P + "term/run", views.term_run),
    path(P + "term/stop", views.term_stop),
    path(P + "term/input", views.term_input),
    path(P + "term/clear", views.term_clear),
    path(P + "term/output", views.term_output),
]
