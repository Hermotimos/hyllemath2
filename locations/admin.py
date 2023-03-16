from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import TextField, CharField, ForeignKey, Max
from django.forms import ModelForm, Select, Textarea, TextInput
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse

from characters.admin_filters import (
    FirstNameGroupOfFirstNameFilter, ParentgroupOfFirstNameGroupFilter,
)
from locations.models import  (
    LocationNameTag, LocationName, LocationType, Location, LocationVersion,
)
from myproject.utils_admin import (
    CustomModelAdmin, CachedFormfieldsFKMixin, CachedFormfieldsAllMixin,
    get_count_color, TagAdminForm, VersionedAdminMixin,
)


@admin.register(LocationNameTag)
class LocationNameTagAdmin(CustomModelAdmin):
    fields = ['title', 'color', 'ordernum']
    form = TagAdminForm
    list_display = ['id', 'title', 'color', 'ordernum']
    list_editable = fields


#  ------------------------------------------------------------


@admin.register(LocationName)
class LocationNameAdmin(CustomModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                ('nominative', 'genitive', 'adjectiveroot'),
                'equivalents',
                'description',
                'tags'
            ),
        }),
    ]
    filter_horizontal = ['tags']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
        CharField: {'widget': TextInput(attrs={'size': 20})},
    }
    list_display = [
        'id', 'nominative', 'genitive', 'adjectiveroot', 'equivalents',
        'description',
    ]
    list_editable = [
        'nominative', 'genitive', 'adjectiveroot', 'equivalents',
        'description',
    ]
    prepopulated_fields = {
        'genitive': ['nominative'],
        'adjectiveroot': ['nominative']
    }
    search_fields = ['nominative', 'adjectiveroot']


#  ------------------------------------------------------------


@admin.register(LocationType)
class LocationTypeAdmin(CustomModelAdmin):
    list_display = ['id', 'hierarchynum','name', 'namepl', 'defaultpicture']
    list_editable = ['hierarchynum', 'name', 'namepl', 'defaultpicture']


#  ------------------------------------------------------------


# TODO LocationVersionInline

@admin.register(Location)
class LocationAdmin(CustomModelAdmin, VersionedAdminMixin):
    xxxx = "hhd"
    fields = ['user', '_createdat']
    # inlines = [LocationVersionInline]
    list_display = [
        'name', 'propername', 'descriptivename', 'versions', 'locationtype',
    ]
    list_editable = ['propername', 'descriptivename', 'locationtype']
    readonly_fields = ['name']
