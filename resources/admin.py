from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from myproject.utils_admin import CustomModelAdmin, related_objects_change_list_link
from resources.models import Picture


@admin.register(Picture)
class PictureAdmin(CustomModelAdmin):
    list_display = [
        'title', 'characterversions_link', 'locationversions_link',
        'category', 'image',
    ]
    list_editable = ['image']
    list_filter = ['category']
    search_fields = ['title', 'image']

    @admin.display(description="Character Versions")
    def characterversions_link(self, obj):
        return related_objects_change_list_link(obj, obj.characterversions)

    @admin.display(description="Location Versions")
    def locationversions_link(self, obj):
        return related_objects_change_list_link(obj, obj.locationversions)


    # TODO: podobne dodatkowe pola z linkiem dla innych obiektów z picture:
    #  (PictureVersion, PictureSet) - metoda, nadpiska nazwy, prefetch
