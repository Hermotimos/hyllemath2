from django.conf import settings
from django.contrib import admin
from django.db.models import TextField, CharField, ForeignKey, Max
from django.forms import ModelForm, Select, Textarea, TextInput
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse

from characters.admin_filters import (
    FirstNameGroupOfFirstNameFilter, ParentgroupOfFirstNameGroupFilter,
)
from characters.models import (
    Character,  Relationship,
    CharacterVersion, CharacterVersionTag,
    FamilyName, FamilyNameGroup, FamilyNameTag,
    FirstName, FirstNameGroup, FirstNameTag
)
from myproject.utils_admin import (
    CachedFormfieldsFK, CachedFormfieldsM2M, CachedFormfieldsAll,
    get_count_color,
)
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


class FirstNameInline(CachedFormfieldsAll, admin.TabularInline):
    model = FirstName
    extra = 10
    fields = [
        'nominative', 'genitive', 'gender', 'isarchaic', 'origin',
        'meaning', 'description', 'comments', 'equivalents', 'tags',
    ]
    filter_horizontal = ['tags', 'equivalents']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 14})},
        CharField: {'widget': TextInput(attrs={'size': 12})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:120px'})},
    }


@admin.register(FirstNameGroup)
class FirstNameGroupAdmin(CachedFormfieldsFK, admin.ModelAdmin):
    inlines = [FirstNameInline]
    list_display = ['id', 'title', 'parentgroup', 'description']
    list_editable = ['title', 'parentgroup', 'description']
    list_filter = [ParentgroupOfFirstNameGroupFilter]

    class Media:
        css = {
            'all': (f'{settings.STATIC_URL}css/admin_change_form_namegroup.css',)
        }


@admin.register(FirstName)
class FirstNameAdmin(CachedFormfieldsFK, admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                ('firstnamegroup', 'gender', 'isarchaic'),
                ('nominative', 'genitive', 'origin'),
                ('meaning', 'description', 'comments',),
                'equivalents',
                'tags'
            ),
        }),
    ]
    filter_horizontal = ['tags', 'equivalents']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 20})},
        CharField: {'widget': TextInput(attrs={'size': 10})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    list_display = [
        'id', 'nominative', 'genitive', 'gender', 'isarchaic', 'firstnamegroup',
        'origin', 'meaning', 'description', 'comments',
    ]
    list_editable = [
        'nominative', 'genitive', 'gender', 'isarchaic', 'firstnamegroup',
        'origin', 'meaning', 'description', 'comments',
    ]
    list_filter = ['gender', FirstNameGroupOfFirstNameFilter]
    list_per_page = 50
    prepopulated_fields = {'genitive': ['nominative']}
    search_fields = ['nominative', 'description']


#  ------------------------------------------------------------



class FamilyNameInline(CachedFormfieldsAll, admin.TabularInline):
    model = FamilyName
    extra = 5
    fields = [
        'origin', 'nominative', 'nominative_pl', 'genitive',
        'genitive_pl', 'description', 'tags',
    ]
    filter_horizontal = ['tags']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 14})},
        CharField: {'widget': TextInput(attrs={'size': 12})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:120px'})},
    }

    class Media:
        css = {
            'all': (f'{settings.STATIC_URL}css/admin_change_form_namegroup.css',)
        }


@admin.register(FamilyNameGroup)
class FamilyNameGroupAdmin(admin.ModelAdmin):
    inlines = [FamilyNameInline]
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


@admin.register(FamilyName)
class FamilyNameAdmin(CachedFormfieldsFK, admin.ModelAdmin):
    filter_horizontal = ['tags']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    list_display = [
        'id', 'origin', 'nominative', 'nominative_pl', 'genitive',
        'genitive_pl', 'description',
    ]
    list_editable = [
        'origin', 'nominative', 'nominative_pl', 'genitive', 'genitive_pl',
        'description',
    ]
    prepopulated_fields = {
        'nominative_pl': ['nominative'],
        'genitive': ['nominative'],
        'genitive_pl': ['nominative'],
    }
    search_fields = ['nominative', 'description']


#  ------------------------------------------------------------


class RelationshipInlineForCharacter(CachedFormfieldsFK, admin.TabularInline):
    """
    An inline for handling Relationships from Character's perspective.
    That is - which CharacterVersions this Character knows.
    This is different from CharacterVersionRelationshipInline, which is for
    handling Characters who know this CharacterVersion.
    """
    model = Relationship
    fk_name = 'character'


@admin.register(Character)
class CharacterAdmin(CachedFormfieldsFK, admin.ModelAdmin):
    fields = ['user', '_createdat']
    inlines = [RelationshipInlineForCharacter]
    list_display = [
        'id', 'main_characterversion', 'user', 'get_related_characterversions',
        '_createdat',
    ]
    list_editable = ['user']
    readonly_fields = ['_createdat']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('characterversions')
        qs = qs.annotate(main_characterversion=Max('characterversions__fullname'))
        return qs

    def main_characterversion(self, obj):
        return obj.main_characterversion

    def get_related_characterversions(self, obj):
        if count := obj.characterversions.count():
            url = (
                reverse("admin:characters_characterversion_changelist")
                + "?"
                + urlencode({"character__id": f"{obj.id}"})
            )
            color = get_count_color(count)
            html = '<a href="{}" style="border: 1px solid; padding: 2px 3px; color: {};">{}</a>'
            return format_html(html, url, color, count)
        return "-"

    main_characterversion.short_description = "Main Character Version "
    get_related_characterversions.short_description = "Character Versions"



class RelationshipInlineForCharacterVersion(CachedFormfieldsAll, admin.TabularInline):
    """
    An inline for handling Relationships from CharacterVersion's perspective.
    That is - which Characters know this CharacterVersion.
    This is different from CharacterRelationshipInline, which is for
    handling CharacterVersions known by this Character .
    """
    model = CharacterVersion.known_by_characters.through
    fk_name = 'characterversion'
    extra = 2


@admin.register(CharacterVersion)
class CharacterVersionAdmin(CachedFormfieldsFK, admin.ModelAdmin):
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
    inlines = [RelationshipInlineForCharacterVersion]
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
    list_per_page = 50
    readonly_fields = [
        'fullname', '_createdat'
    ]
    search_fields = ['fullname']

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

    get_img.short_description = "Image"
