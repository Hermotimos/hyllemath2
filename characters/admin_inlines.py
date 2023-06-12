from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import TextField, CharField, ForeignKey
from django.forms import Select, Textarea, TextInput
from django.utils.html import format_html

from characters.models import  (
    CharacterVersion, FamilyName, FirstName, Knowledge,
)
from myproject.utils_admin import (
    CachedFKFormfieldMixin, CachedFormfieldsAllMixin, INLINE_HEADER,
)



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

    class Media:
        css = {
            'all': (
                f'{settings.STATIC_URL}css/admin_change_form__M2M_small.css',
                f'{settings.STATIC_URL}css/admin_change_form__namegroup.css',
            )
        }


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
            'all': (
                f'{settings.STATIC_URL}css/admin_change_form__M2M_small.css',
                f'{settings.STATIC_URL}css/admin_change_form__namegroup.css',
            )
        }


#  ------------------------------------------------------------


class CharacterVersionInline(CachedFormfieldsAllMixin, admin.TabularInline):
    fields = [
        'get_img', 'versionkind', 'versioncomment', 'isalive', 'isalterego',
        'firstname', 'familyname', 'nickname', 'originname',
        'description', 'picture', '_createdat',
    ]
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 5, 'cols': 30})},
        CharField: {'widget': TextInput(attrs={'size': 10})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:150px'})},
    }
    model = CharacterVersion
    extra = 1
    fk_name = 'character'
    readonly_fields = ['get_img', '_createdat']

    @admin.display(description="Image")
    def get_img(self, obj):
        img = '<img src="{}" width="70" height="70">'
        comment = '<br><span style="color: red; font-weight: normal; font-style: italic;">{}</span>'
        html = img + comment if obj.versioncomment else img
        if obj.picture:
            return format_html(html, obj.picture.image.url, obj.versioncomment)
        return format_html(html, "media/profile_pics/profile_default.jpg", obj.versioncomment)


#  ------------------------------------------------------------


class ContentTypeKnowledgeInline(CachedFKFormfieldMixin, admin.TabularInline):
    content_type_model = ''     # override in concrete implementations
    model = Knowledge

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('content_object')
        qs = qs.filter(content_type__model__iexact=self.content_type_model)
        return qs


class CharacterVersionKnowledgeInline(ContentTypeKnowledgeInline):
    content_type_model = "CharacterVersion"
    verbose_name_plural = format_html(
        INLINE_HEADER, 'Knowledges', 'CharacterVersions known by this Character')


class LocationVersionKnowledgeInline(ContentTypeKnowledgeInline):
    content_type_model = "LocationVersion"
    verbose_name_plural = format_html(
        INLINE_HEADER, 'Knowledges', 'LocationVersions known by this Character')


class InfoItemVersionKnowledgeInline(ContentTypeKnowledgeInline):
    content_type_model = "InfoItemVersion"
    verbose_name_plural = format_html(
        INLINE_HEADER, 'Knowledges', 'InfoItemVersions known by this Character')

    def get_queryset(self, request):
        """
        Override method to achieve prefetch. This is necessary as long as
        InfoItemVersion has no title and uses InfoItem.title for __str__.
        """
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('content_object__infoitem')
        qs = qs.filter(content_type__model__iexact=self.content_type_model)
        return qs


#  ------------------------------------------------------------


class BasePassiveKnowledgeInline(CachedFKFormfieldMixin, GenericTabularInline):
    model = Knowledge

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('content_object')
        return qs


class CharacterVersionPassiveKnowledgeInline(BasePassiveKnowledgeInline):
    verbose_name_plural = format_html(
        INLINE_HEADER, 'Knowledges', 'Characters knowing this CharacterVersion')


#  ------------------------------------------------------------
