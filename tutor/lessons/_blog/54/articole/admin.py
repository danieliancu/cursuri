from django.contrib import admin

from .models import Articol, Categorie, Comentariu, Eticheta


class ComentariuInline(admin.TabularInline):
    model = Comentariu
    extra = 0


@admin.register(Articol)
class ArticolAdmin(admin.ModelAdmin):
    list_display = ["titlu", "categorie", "data_publicarii", "publicat"]
    list_filter = ["publicat", "categorie"]
    search_fields = ["titlu", "continut"]
    inlines = [ComentariuInline]


@admin.register(Comentariu)
class ComentariuAdmin(admin.ModelAdmin):
    list_display = ["autor", "articol", "data"]
    search_fields = ["autor", "text"]


admin.site.register(Categorie)
admin.site.register(Eticheta)
