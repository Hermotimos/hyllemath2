from django.contrib import admin

from resources.models import Picture


@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image']
    list_editable = ['title', 'image']

