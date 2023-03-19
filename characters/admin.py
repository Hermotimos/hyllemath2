from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import TextField, CharField, ForeignKey, Min
from django.forms import Select, Textarea, TextInput
from django.utils.html import format_html

from characters.admin_filters import (
    FirstNameGroupOfFirstNameFilter, ParentgroupOfFirstNameGroupFilter,
)
from characters.models import  (
    Character,
    CharacterVersion, CharacterVersionTag,
    FamilyName, FamilyNameGroup, FamilyNameTag,
    FirstName, FirstNameGroup, FirstNameTag,
    Knowledge,
)
from myproject.utils_admin import (
    CustomModelAdmin, CachedFormfieldsFKMixin, CachedFormfieldsAllMixin,
    TagAdminForm, VersionedAdminMixin,
)



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
        'meaning', 'description', 'equivalents', 'tags', '_comment',
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
            'all': (f'{settings.STATIC_URL}css/admin_change_form_namegroup.css',)
        }


@admin.register(FirstName)
class FirstNameAdmin(CustomModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                ('firstnamegroup', 'gender', 'isarchaic'),
                ('nominative', 'genitive', 'origin'),
                ('meaning', 'description'),
                'equivalents',
                'tags'
                '_comment'
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
        'origin', 'meaning', 'description', '_comment',
    ]
    list_editable = [
        'nominative', 'genitive', 'gender', 'isarchaic', 'firstnamegroup',
        'origin', 'meaning', 'description', '_comment',
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
        'nominative', 'nominative_pl', 'genitive', 'genitive_pl', 'origin',
        'description', 'tags', '_comment',
    ]
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
        'genitive_pl', 'description', '_comment',
    ]
    list_editable = [
        'origin', 'nominative', 'nominative_pl', 'genitive', 'genitive_pl',
        'description', '_comment',
    ]
    prepopulated_fields = {
        'nominative_pl': ['nominative'],
        'genitive': ['nominative'],
        'genitive_pl': ['nominative'],
    }
    search_fields = ['nominative', 'description']


#  ------------------------------------------------------------


class CharacterVersionInline(CachedFormfieldsAllMixin, admin.TabularInline):
    fields = [
        'fullname', 'versionkind', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description',
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    model = CharacterVersion
    extra = 1
    fk_name = 'character'
    readonly_fields = ['fullname']


class KnowledgeActiveInline(CachedFormfieldsFKMixin, admin.TabularInline):
    # Regular admin.TabularInline for this side of the generic relation!
    model = Knowledge
    verbose_name_plural = "Knowledges (this character knows these character versions)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('content_object')
        return qs


@admin.register(Character)
class CharacterAdmin(CustomModelAdmin, VersionedAdminMixin):
    fieldsets = [
        (None, {
            'fields': (
                '_mainversionname',
                'user',
                ('strength', 'dexterity', 'endurance', 'power',),
                'experience',
                '_createdat',
            )
        }),
    ]
    inlines = [CharacterVersionInline, KnowledgeActiveInline]
    list_display = [
        '_mainversionname', '_versions', 'user',
        'strength', 'dexterity', 'endurance', 'power', 'experience',
        '_createdat',
    ]
    list_editable = [
        'user', 'strength', 'dexterity', 'endurance', 'power', 'experience',
    ]
    readonly_fields = ['_mainversionname', '_createdat']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('characterversions')
        return qs


#  ------------------------------------------------------------


class KnowledgePassiveInline(CachedFormfieldsFKMixin, GenericTabularInline):
    model = Knowledge
    # fk_name = 'character'
    verbose_name_plural = "Knowledges (this character version is known by these characters)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('content_object')
        return qs


@admin.register(CharacterVersion)
class CharacterVersionAdmin(CustomModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'fullname',
                ('character', 'picture'),
                ('firstname', 'familyname', 'nickname', 'originname',),
                ('_comment', 'versionkind', 'isalive', 'isalterego'),
                'description',
                'tags',
                ('_createdat', '_createdby'),
            )
        }),
    ]
    filter_horizontal = ['tags']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    inlines = [KnowledgePassiveInline]
    list_display = [
        'get_img', 'fullname', 'versionkind', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description',
        '_createdby', '_comment', '_createdat',
    ]
    list_editable = [
        'versionkind', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description', '_comment'
    ]
    list_per_page = 50
    radio_fields =  {"versionkind": admin.VERTICAL}
    readonly_fields = [
        'fullname', '_createdat', '_createdby',
    ]
    search_fields = ['fullname']

    class Media:
        css = {
            'all': (f'{settings.STATIC_URL}css/admin_change_form_characterversion.css',)
        }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Show only tags created by GMs
        if db_field.name == "tags":
            kwargs["queryset"] = CharacterVersionTag.objects.filter(user__is_staff=True)
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
        html = img + comment if obj._comment else img
        if obj.picture:
            return format_html(html, obj.picture.image.url, obj._comment)
        return format_html(html, "media/profile_pics/profile_default.jpg", obj._comment)
