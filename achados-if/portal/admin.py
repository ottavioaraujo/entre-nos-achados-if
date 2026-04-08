from django.contrib import admin

from .models import CampusItem


@admin.register(CampusItem)
class CampusItemAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "category", "location", "event_date", "reporter", "is_resolved", "created_at")
    list_filter = ("kind", "category", "is_resolved")
    search_fields = ("name", "location", "description", "contact_phone")
    date_hierarchy = "created_at"
