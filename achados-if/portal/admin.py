from django.contrib import admin

from .models import CampusItem, CampusItemComment


@admin.register(CampusItem)
class CampusItemAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "category", "location", "event_date", "reporter", "is_resolved", "created_at")
    list_filter = ("kind", "category", "is_resolved")
    search_fields = ("name", "location", "description", "contact_phone")
    date_hierarchy = "created_at"
    exclude = ("photo", "photo_data", "photo_content_type")


@admin.register(CampusItemComment)
class CampusItemCommentAdmin(admin.ModelAdmin):
    list_display = ("item", "author", "created_at")
    search_fields = ("body", "author", "item__name")
    readonly_fields = ("created_at",)
