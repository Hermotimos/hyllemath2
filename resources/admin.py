from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from myproject.utils_admin import get_count_color
from resources.models import Picture


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image', 'get_related_characterversions']
    list_editable = ['title', 'image']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('characterversions')

    @admin.display(description="Character Versions")
    def get_related_characterversions(self, obj):
        if count := obj.characterversions.count():
            url = (
                reverse("admin:characters_characterversion_changelist")
                + "?"
                + urlencode({"picture__id": f"{obj.id}"})
            )
            color = get_count_color(count)
            html = '<a href="{}" style="border: 1px solid; padding: 2px 3px; color: {};">{}</a>'
            return format_html(html, url, color, count)
        return "-"

    # TODO: podobne dodatkowe pola z linkiem dla innych obiektów z picture:
    #  (PictureVersion, PictureSet) - metoda, nadpiska nazwy, prefetch