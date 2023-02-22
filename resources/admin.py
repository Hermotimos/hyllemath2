from django.contrib import admin

from resources.models import Picture, Tag



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'color']
    list_editable = ['author', 'title', 'color']


@admin.register(Picture)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image']
    list_editable = ['title', 'image']


