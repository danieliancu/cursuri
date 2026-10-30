from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Max, Sum
from django.urls import reverse
from django.utils.html import format_html

from . import workspace
from .models import (
    LESSON_MANUAL,
    STATUS_DONE,
    ChatMessage,
    Conversation,
    CostSettings,
    ModelPrice,
    Module,
    StudentProfile,
    Topic,
    TopicCode,
    TopicEvidence,
    TopicProgress,
    UsageRecord,
)
from .templatetags.pytutor import format_gbp


def gbp(usd, rate) -> str:
    return format_gbp((usd or 0) * rate)


# --- Utilizatori, cu costul AI în listă ---

admin.site.unregister(User)


@admin.register(User)
class PyTutorUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "is_staff", "is_active", "ai_calls", "ai_cost", "last_ai", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _calls=Count("ai_usage"), _cost=Sum("ai_usage__cost_usd"), _last=Max("ai_usage__created_at")
        )

    def changelist_view(self, request, extra_context=None):
        self._rate = CostSettings.get().usd_to_gbp
        return super().changelist_view(request, extra_context)

    @admin.display(description="apeluri AI", ordering="_calls")
    def ai_calls(self, obj):
        return obj._calls

    @admin.display(description="cost AI (GBP)", ordering="_cost")
    def ai_cost(self, obj):
        url = reverse("admin:tutor_usagerecord_changelist") + f"?user__id__exact={obj.pk}"
        return format_html('<a href="{}">{}</a>', url, gbp(obj._cost, getattr(self, "_rate", 1)))

    @admin.display(description="ultimul apel AI", ordering="_last")
    def last_ai(self, obj):
        return obj._last or "—"


# --- Consum ---

@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "project", "model", "input_tokens", "output_tokens",
                    "cache_read_tokens", "cost_gbp", "priced")
    list_filter = ("provider", "model", "priced", ("user", admin.RelatedOnlyFieldListFilter))
    date_hierarchy = "created_at"
    search_fields = ("user__username", "project", "model")
    list_select_related = ("user",)

    def changelist_view(self, request, extra_context=None):
        self._rate = CostSettings.get().usd_to_gbp
        return super().changelist_view(request, extra_context)

    @admin.display(description="cost (GBP)", ordering="cost_usd")
    def cost_gbp(self, obj):
        return gbp(obj.cost_usd, getattr(self, "_rate", 1))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ModelPrice)
class ModelPriceAdmin(admin.ModelAdmin):
    list_display = ("model", "input_usd", "output_usd", "cache_read_usd", "cache_write_usd")
    list_editable = ("input_usd", "output_usd", "cache_read_usd", "cache_write_usd")


@admin.register(CostSettings)
class CostSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__",)

    def has_add_permission(self, request):
        return not CostSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "level", "mastered", "projects", "updated_at")
    search_fields = ("user__username", "user__first_name", "level", "summary")
    readonly_fields = ("updated_at", "projects")
    exclude = ("topics",)
    list_select_related = ("user",)

    @admin.display(description="subiecte învățate")
    def mastered(self, obj):
        url = reverse("admin:tutor_topicprogress_changelist") + f"?user__id__exact={obj.user_id}"
        n = TopicProgress.objects.filter(user=obj.user, status=STATUS_DONE).count()
        return format_html('<a href="{}">{} / {}</a>', url, n, Topic.objects.count())

    @admin.display(description="proiecte")
    def projects(self, obj):
        return ", ".join(workspace.list_projects(obj.user)) or "—"


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    fields = ("created_at", "role", "is_tool_result", "preview")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = False

    @admin.display(description="conținut")
    def preview(self, obj):
        if obj.ui_text:
            return obj.ui_text[:300]
        texts = [b.get("text", "") for b in obj.content if isinstance(b, dict) and b.get("type") == "text"]
        tools = [b.get("name", "") for b in obj.content if isinstance(b, dict) and b.get("type") == "tool_use"]
        out = " ".join(texts)[:300]
        if tools:
            out += f"  [unelte: {', '.join(tools)}]"
        return out or "—"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "message_count", "created_at")
    list_filter = ("user",)
    search_fields = ("user__username", "project")
    inlines = [ChatMessageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_n=Count("messages"))

    @admin.display(description="mesaje", ordering="_n")
    def message_count(self, obj):
        return obj._n


# --- Curriculum și progres ---

class TopicInline(admin.TabularInline):
    model = Topic
    fields = ("order", "slug", "title", "has_lesson")
    readonly_fields = ("has_lesson",)
    extra = 0
    show_change_link = True

    @admin.display(description="lecție", boolean=True)
    def has_lesson(self, obj):
        return bool(obj.lesson)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "slug", "topic_count")
    list_display_links = ("title",)
    inlines = [TopicInline]

    @admin.display(description="subiecte")
    def topic_count(self, obj):
        return obj.topics.count()


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "slug", "has_lesson", "lesson_model", "lesson_updated_at")
    list_filter = ("module", "lesson_model")
    search_fields = ("title", "slug", "summary", "lesson")
    readonly_fields = ("lesson_model", "lesson_updated_at")
    actions = ["clear_lesson"]

    def get_readonly_fields(self, request, obj=None):
        # o lecție manuală editată aici s-ar pierde la următorul `load_lessons`: se editează fișierul
        if obj and obj.lesson_model == LESSON_MANUAL:
            return (*self.readonly_fields, "lesson")
        return self.readonly_fields

    @admin.display(description="lecție", boolean=True)
    def has_lesson(self, obj):
        return bool(obj.lesson)

    @admin.action(description="Șterge lecția (AI-ul o rescrie la următoarea deschidere)")
    def clear_lesson(self, request, queryset):
        manual = queryset.filter(lesson_model=LESSON_MANUAL).count()
        n = queryset.exclude(lesson_model=LESSON_MANUAL).update(lesson="", lesson_model="", lesson_updated_at=None)
        msg = f"{n} lecții vor fi rescrise."
        if manual:
            msg += f" {manual} sunt scrise în proiect și se editează în tutor/lessons/."
        self.message_user(request, msg)


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "status", "updated_at")
    list_filter = ("status", "topic__module", ("user", admin.RelatedOnlyFieldListFilter))
    search_fields = ("user__username", "topic__title")
    list_select_related = ("user", "topic", "topic__module")


@admin.register(TopicEvidence)
class TopicEvidenceAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "topic", "status", "path", "short_comment")
    list_filter = ("status", "topic__module", ("user", admin.RelatedOnlyFieldListFilter))
    search_fields = ("user__username", "topic__title", "comment", "code")
    list_select_related = ("user", "topic")
    date_hierarchy = "created_at"

    @admin.display(description="ce a spus tutorele")
    def short_comment(self, obj):
        return obj.comment[:120]


@admin.register(TopicCode)
class TopicCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "project", "path", "updated_at")
    list_filter = ("topic__module", ("user", admin.RelatedOnlyFieldListFilter))
    search_fields = ("user__username", "topic__title", "path", "content")
    list_select_related = ("user", "topic")
