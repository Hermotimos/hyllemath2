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
    CustomModelAdmin, CachedFormfieldsFKMixin, CachedFormfieldsAllMixin,
    get_count_color,
)


class TagAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add widget for a field identified by name
        # it can be done in Meta, but then fields/exclude must be defined
        self.fields['color'].widget = TextInput(attrs={'type': 'color'})


@admin.register(FirstNameTag, FamilyNameTag)
class TagGMAdmin(CustomModelAdmin):
    fields = ['title', 'color']
    form = TagAdminForm
    list_display = ['id', 'title', 'color']
    list_editable = fields


@admin.register(CharacterVersionTag)
class TagAdmin(CustomModelAdmin):
    fields = ['user', 'title', 'color']
    form = TagAdminForm
    list_display = ['id', 'user', 'title', 'color']
    list_editable = fields

    def get_changeform_initial_data(self, request):
        # Set user FK field to the requesting user in 'add form'.
        return {'user': request.user}


#  ------------------------------------------------------------


class FirstNameInline(CachedFormfieldsAllMixin, admin.TabularInline):
    filter_horizontal = ['tags', 'equivalents']
    model = FirstName
    extra = 5
    fields = [
        'nominative', 'genitive', 'gender', 'isarchaic', 'origin',
        'meaning', 'description', 'comments', 'equivalents', 'tags',
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 14})},
        CharField: {'widget': TextInput(attrs={'size': 12})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:120px'})},
    }


@admin.register(FirstNameGroup)
class FirstNameGroupAdmin(CustomModelAdmin):
    inlines = [FirstNameInline]
    list_display = ['id', 'title', 'parentgroup', 'description']
    list_editable = ['title', 'parentgroup', 'description']
    list_filter = [ParentgroupOfFirstNameGroupFilter]

    class Media:
        css = {
            'all': ('admin_change_form_namegroup.css',)
        }


@admin.register(FirstName)
class FirstNameAdmin(CustomModelAdmin):
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
    filter_horizontal = ['equivalents', 'tags']
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



class FamilyNameInline(CachedFormfieldsAllMixin, admin.TabularInline):
    filter_horizontal = ['tags']
    model = FamilyName
    extra = 5
    fields = [
        'origin', 'nominative', 'nominative_pl', 'genitive',
        'genitive_pl', 'description', 'tags',
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 14})},
        CharField: {'widget': TextInput(attrs={'size': 12})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:120px'})},
    }

    class Media:
        css = {
            'all': ('admin_change_form_namegroup.css',)
        }


@admin.register(FamilyNameGroup)
class FamilyNameGroupAdmin(CustomModelAdmin):
    inlines = [FamilyNameInline]
    list_display = ['id', 'title', 'description']
    list_editable = ['title', 'description']


@admin.register(FamilyName)
class FamilyNameAdmin(CustomModelAdmin):
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


class RelationshipInlineForCharacter(CachedFormfieldsFKMixin, admin.TabularInline):
    """
    An inline for handling Relationships from Character's perspective.
    That is - which CharacterVersions this Character knows.
    This is different from CharacterVersionRelationshipInline, which is for
    handling Characters who know this CharacterVersion.
    """
    model = Relationship
    fk_name = 'character'


@admin.register(Character)
class CharacterAdmin(CustomModelAdmin):
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

    @admin.display(description="Character Versions")
    def main_characterversion(self, obj):
        return obj.main_characterversion

    @admin.display(description="Main Character Version")
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


#  ------------------------------------------------------------


class RelationshipInlineForCharacterVersion(CachedFormfieldsFKMixin, admin.TabularInline):
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
class CharacterVersionAdmin(CustomModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                ('character', 'picture'),
                'fullname',
                ('comment', 'versionkind', 'isalive', 'isalterego'),
                ('firstname', 'familyname', 'nickname', 'originname',),
                'description',
                ('strength', 'dexterity', 'endurance', 'power',),
                'experience',
                'tags',
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
    radio_fields =  {"versionkind": admin.VERTICAL}
    readonly_fields = [
        'fullname', '_createdat',
    ]
    search_fields = ['fullname']

    class Media:
        css = {
            'all': ('admin_change_form_characterversion.css',)
        }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Show only tags created by GMs
        if db_field.name == "tags":
            kwargs["queryset"] = CharacterVersionTag.objects.filter(
                user__is_staff=True
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        # hide all inlines in the add view, see get_formsets_with_inlines:
        # https://docs.djangoproject.com/en/4.1/ref/contrib/admin/
        for inline in self.get_inline_instances(request, obj):
            if obj is not None:
                yield inline.get_formset(request, obj), inline

    @admin.display(description="Image")
    def get_img(self, obj):
        img = '<img src="{}" width="70" height="70">'
        comment = '<br><span style="color: red; font-weight: normal; font-style: italic;">{}</span>'
        html = img + comment if obj.comment else img
        if obj.picture:
            return format_html(html, obj.picture.image.url, obj.comment)
        return format_html(html, "media/profile_pics/profile_default.jpg", obj.comment)
