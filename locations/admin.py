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


class LocationVersionInline(CachedFormfieldsAllMixin, admin.TabularInline):
    fields = [
        'versionkind', 'location', 'propername', 'descriptivename',
        'population', 'picture', 'description', '_comment',
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    model = LocationVersion
    extra = 1


@admin.register(Location)
class LocationAdmin(CustomModelAdmin, VersionedAdminMixin):
    fieldsets = [
        (None, {
            'fields': (
                '_mainversionname',
                'locationtype',
                'inlocation',
                '_createdat',
            )
        }),
    ]
    inlines = [LocationVersionInline]
    list_display = [
        '_mainversionname', '_versions', 'locationtype', 'inlocation',
        '_createdat',
    ]
    list_editable = ['locationtype', 'inlocation', ]
    readonly_fields = ['_mainversionname', '_createdat']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('locationversions')
        return qs


#  ------------------------------------------------------------


@admin.register(LocationVersion)
class LocationVersionAdmin(CustomModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'name',
                ('versionkind', 'location', 'picture'),
                ('propername', 'descriptivename'),
                'population',
                ('description', '_comment'),
                ('_createdat', '_createdby'),
            )
        }),
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 30})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    list_display = [
        'name',
        'versionkind', 'location', 'propername', 'descriptivename', 'population',
        'picture', 'description', '_comment', '_createdby', '_createdat',
    ]
    list_editable = [
        'versionkind', 'location', 'picture', 'propername', 'descriptivename',
        'population', 'description', '_comment',
    ]
    readonly_fields = ['_createdby', '_createdat']

    def get_formsets_with_inlines(self, request, obj=None):
        # hide all inlines in the add view, see get_formsets_with_inlines:
        # https://docs.djangoproject.com/en/4.1/ref/contrib/admin/
        for inline in self.get_inline_instances(request, obj):
            if obj is not None:
                yield inline.get_formset(request, obj), inline

