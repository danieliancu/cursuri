from django.contrib import admin
from django.urls import include, path

from tutor.admin_views import usage_report

admin.site.site_header = "PyTutor — administrare"
admin.site.site_title = "PyTutor admin"
admin.site.index_title = "Elevi, profiluri, conversații și consum AI"

urlpatterns = [
    path("admin/consum/", admin.site.admin_view(usage_report), name="usage_report"),
    path("admin/", admin.site.urls),
    path("", include("tutor.urls")),
]
