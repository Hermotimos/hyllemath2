from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField, BaseModelForm, TextInput

from characters.models import (
    FirstName, FirstNameGroup, FirstNameTag,
    FamilyName, FamilyNameGroup, FamilyNameTag,
    Character, CharacterVersion, CharacterVersionTag,
    # CharacterRelationship,
)

from myproject.utils_models import Tag
from myproject.utils_admin import formfield_with_cache


class TagAdminForm(ModelForm):

    class Meta:
        model = Tag
        exclude = []
        widgets = {'color': TextInput(attrs={'type': 'color'})}


@admin.register(FirstNameTag, FamilyNameTag, CharacterVersionTag)
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
class FirstNameAdmin(admin.ModelAdmin):
    filter_horizontal = ['tags']
    list_display = [
        'id', 'gender', 'origin', 'nominative', 'genitive', 'description',
    ]
    list_editable = [
        'gender', 'origin', 'nominative', 'genitive', 'description',
    ]


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
class CharacterAdmin(admin.ModelAdmin):
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
class CharacterVersionAdmin(admin.ModelAdmin):
    fields = [
        'character', 'versionkind', 'picture', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname', 'fullname',
        'description',
        'strength', 'dexterity', 'endurance', 'power', 'experience', 'tags',
    ]
    filter_horizontal = ['tags']
    inlines = [CharacterVersionRelationshipInline]
    list_display = [
        'id', 'character', 'versionkind', 'picture', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname', 'fullname',
        'description',
        'strength', 'dexterity', 'endurance', 'power', 'experience',
        '_createdat',
    ]
    list_editable = [
        'character', 'versionkind', 'picture', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description',
        'strength', 'dexterity', 'endurance', 'power', 'experience',
    ]
    readonly_fields = [
        'fullname', '_createdat'
    ]

