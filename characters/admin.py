from django.conf import settings
from django.contrib import admin
from django.db.models import TextField, CharField, ForeignKey
from django.forms import ModelForm, Select, Textarea, TextInput
from django.utils.html import format_html

from characters.admin_filters import FirstNameGroupAdminFilter
from characters.models import (
    Character,  # Relationship,
    CharacterVersion, CharacterVersionTag,
    FamilyName, FamilyNameGroup, FamilyNameTag,
    FirstName, FirstNameGroup, FirstNameTag
)
from myproject.utils_admin import CachedFormfieldForFKMixin
from myproject.utils_models import Tag


class TagAdminForm(ModelForm):

    class Meta:
        model = Tag
        exclude = []
        widgets = {'color': TextInput(attrs={'type': 'color'})}


@admin.register(FirstNameTag, FamilyNameTag)
class TagGMAdmin(admin.ModelAdmin):
    fields = ['title', 'color']
    form = TagAdminForm
    list_display = ['id', 'title', 'color']
    list_editable = fields


@admin.register(CharacterVersionTag)
class TagAdmin(admin.ModelAdmin):
    fields = ['user', 'title', 'color']
    form = TagAdminForm
    list_display = ['id', 'user', 'title', 'color']
    list_editable = fields


#  ------------------------------------------------------------


@admin.register(FirstNameGroup)
class FirstNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


@admin.register(FirstName)
class FirstNameAdmin(CachedFormfieldForFKMixin, admin.ModelAdmin):
    filter_horizontal = ['tags']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 20})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:180px'})},
    }
    list_display = [
        'id', 'nominative', 'genitive', 'gender', 'firstnamegroup', 'origin',
        'description',
    ]
    list_editable = [
        'nominative', 'genitive', 'gender', 'origin', 'firstnamegroup',
        'description',
    ]
    list_filter = ['gender', FirstNameGroupAdminFilter]
    search_fields = ['nominative', 'description']


#  ------------------------------------------------------------


@admin.register(FamilyNameGroup)
class FamilyNameGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


@admin.register(FamilyName)
class FamilyNameAdmin(admin.ModelAdmin):
    filter_horizontal = ['tags']
    list_display = [
        'id', 'origin', 'nominative', 'nominative_pl', 'genitive',
        'genitive_pl', 'description',
    ]
    list_editable = [
        'origin', 'nominative', 'nominative_pl', 'genitive', 'genitive_pl',
        'description',
    ]


#  ------------------------------------------------------------


class CharacterRelationshipInline(admin.TabularInline):
    """
    An inline for handling Relationships from Charcter's perspective.
    That is - which CharacterVersions this Character knows.
    This is different from CharacterVersionRelationshipInline, which is for
    handling Characters who know this CharacterVersion.
    """
    model = Character.relationships.through
    fk_name = 'character'

    # TODO: optimize inline: 1. migrate data, 2. optimize with real db records

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     print(qs)
    #     return qs.prefetch_related('character__characterversions').select_related('character__user', 'characterversion')

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
    #     for field in [
    #         'character',
    #         'characterversion',
    #     ]:
    #         if db_field.name == field:
    #             formfield = formfield_with_cache(field, formfield, request)
    #     return formfield


@admin.register(Character)
class CharacterAdmin(CachedFormfieldForFKMixin, admin.ModelAdmin):
    fields = ['id', 'user', '_createdat']
    inlines = [CharacterRelationshipInline]
    list_display = fields
    list_editable = ['user']
    readonly_fields = ['id', '_createdat']


class CharacterVersionRelationshipInline(admin.TabularInline):
    """
    An inline for handling Relationships from CharacterVersion's perspective.
    That is - which Characters know this CharacterVersion.
    This is different from CharacterRelationshipInline, which is for
    handling CharacterVersions known by this Character .
    """
    model = CharacterVersion.known_by_characters.through
    fk_name = 'characterversion'

    # TODO: optimize inline: 1. migrate data, 2. optimize with real db records

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     print(qs)
    #     return qs.prefetch_related('character__characterversions').select_related('character__user', 'characterversion')

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
    #     for field in [
    #         'character',
    #         'characterversion',
    #     ]:
    #         if db_field.name == field:
    #             formfield = formfield_with_cache(field, formfield, request)
    #     return formfield


@admin.register(CharacterVersion)
class CharacterVersionAdmin(CachedFormfieldForFKMixin, admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                ('character', 'fullname', 'picture'),
                ('versionkind', 'isalive', 'isalterego',),
                ('firstname', 'familyname', 'nickname', 'originname',),
                'description',
                ('strength', 'dexterity', 'endurance', 'power',),
                'experience',
                'tags'
            )
        }),
    ]
    filter_horizontal = ['tags']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }

    # inlines = [CharacterVersionRelationshipInline]
    list_display = [
        'get_img', 'fullname', 'versionkind', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description',
        'strength', 'dexterity', 'endurance', 'power', 'experience',
    ]
    list_editable = [
        'versionkind', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description',
        'strength', 'dexterity', 'endurance', 'power', 'experience',
    ]
    readonly_fields = [
        'fullname', '_createdat'
    ]

    class Media:
        css = {
            'all': (f'{settings.STATIC_URL}css/admin_change_form_characterversion.css',)
        }


    def get_img(self, obj):
        if obj.picture:
            return format_html(
                f'<img src="{obj.picture.image.url}" width="70" height="70">')
        return format_html(
            '<img src="media/profile_pics/profile_default.jpg" width="70" height="70">')
