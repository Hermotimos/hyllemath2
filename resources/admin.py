from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from resources.models import Picture
from myproject.utils_admin import (
    CustomModelAdmin, CachedFKFormfieldMixin, CachedFormfieldsAllMixin,
    TagAdminForm, VersionedAdminMixin, get_count_color,
)



@admin.register(Picture)
class PictureAdmin(CustomModelAdmin):
    list_display = [
        'title',
        'get_related_characterversions', 'get_related_locationversions',
        'category', 'image',
    ]
    list_editable = ['image']
    list_filter = ['category']
    search_fields = ['title', 'image']

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

    @admin.display(description="Locations")
    def get_related_locationversions(self, obj):
        if count := obj.locationversions.count():
            url = (
                reverse("admin:locations_locationversion_changelist")
                + "?"
                + urlencode({"picture__id": f"{obj.id}"})
            )
            color = get_count_color(count)
            html = '<a href="{}" style="border: 1px solid; padding: 2px 3px; color: {};">{}</a>'
            return format_html(html, url, color, count)
        return "-"

    # TODO: podobne dodatkowe pola z linkiem dla innych obiektów z picture:
    #  (PictureVersion, PictureSet) - metoda, nadpiska nazwy, prefetch