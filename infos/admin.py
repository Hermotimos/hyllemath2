from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import TextField, CharField, ForeignKey, Min
from django.forms import Select, Textarea, TextInput
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from characters.models import Knowledge
from characters.admin_inlines import BasePassiveKnowledgeInline
from infos.models import (
    InfoItem, InfoItemVersion, InfoPacket, InfoPacketSet,
    Reference, InfoItemPosition,
)
from resources.models import PicturePosition
from myproject.utils_admin import (
    CustomModelAdmin, CachedFormfieldsAllMixin, CachedFKFormfieldMixin,
    related_objects_change_list_link, INLINE_HEADER,
)



@admin.register(Reference)
class ReferenceAdmin(CustomModelAdmin):
    list_display = ['id', 'title', 'description', 'url']
    list_editable = ['title', 'description', 'url']
    search_fields = ['title', 'description', 'url']


#  ------------------------------------------------------------


class InfoItemVersionInline(CachedFormfieldsAllMixin, admin.TabularInline):
    fields = [
        'infoitem', 'versionkind', 'versioncomment', 'text', 'references',
    ]
    filter_horizontal = ['references']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 45})},
    }
    model = InfoItemVersion
    extra = 1
    fk_name = 'infoitem'
    readonly_fields = ['__str__', '_createdat']


@admin.register(InfoItem)
class InfoItemAdmin(CustomModelAdmin):
    inlines = [InfoItemVersionInline]
    list_display = [
        'id', 'title', 'infoitemversions_link', 'enigmalevel', '_createdby',
        'isrestricted', '_createdat'
    ]
    list_editable = ['enigmalevel', 'title', 'isrestricted',]
    list_filter = ['enigmalevel', 'isrestricted', '_createdby']
    search_fields = ['title']

    class Media:
        css = {
            'all': (
                f'{settings.STATIC_URL}css/admin_change_form__M2M_medium.css',
                f'{settings.STATIC_URL}css/admin_change_form__namegroup.css',
            )
        }

    @admin.display(description="InfoItem Versions")
    def infoitemversions_link(self, obj):
        return related_objects_change_list_link(obj, obj.infoitemversions)


#  ------------------------------------------------------------


class InfoItemVersionPassiveKnowledgeInline(BasePassiveKnowledgeInline):
    verbose_name_plural = format_html(
        INLINE_HEADER, 'Knowledges', 'Characters knowing this InfoItemVersion')


class PicturePositionInline(CachedFKFormfieldMixin, GenericTabularInline):
    model = PicturePosition
    verbose_name_plural = "Picture Positions"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('content_object')
        return qs


@admin.register(InfoItemVersion)
class InfoItemVersionAdmin(CustomModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'infoitem', 'versionkind',
                ('versioncomment', 'references'),
                ('text', '_createdat'),
            )
        }),
    ]
    filter_horizontal = ['references']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 50})},
        ForeignKey: {'widget': TextInput(attrs={'size': 20})},
    }
    inlines = [PicturePositionInline, InfoItemVersionPassiveKnowledgeInline]
    list_display = [
        'get_infoitem', 'versionkind', 'versioncomment', 'text',
        '_createdat',
    ]
    list_editable = ['versionkind', 'versioncomment', 'text']
    list_filter = ['infoitem__enigmalevel', 'versionkind']
    search_fields = ['text', 'versioncomment']
    readonly_fields = ['_createdat']

    @admin.display(description="InfoItem")
    def get_infoitem(self, obj):
        if len(str(obj.infoitem)) > 70:
            return str(obj.infoitem)[:70] + '...'
        return str(obj.infoitem)


#  ------------------------------------------------------------


class InfoItemPositionInline(CachedFormfieldsAllMixin, admin.TabularInline):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 45})},
    }
    model = InfoItemPosition

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('infoitem', 'infopacket')
        return qs


@admin.register(InfoPacket)
class InfoPacketAdmin(CustomModelAdmin):
    filter_horizontal = ['infoitems']
    inlines = [InfoItemPositionInline]
    list_display = ['id', 'title', 'infopacketkind', 'get_infoitems']
    list_editable = ['title', 'infopacketkind']
    search_fields = ['title']

    @admin.display(description="InfoItems")
    def get_infoitems(self, obj):
        return mark_safe(
            "<br>".join([f"✧ {obj.title}" for obj in obj.infoitems.all()]))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('infoitems')
        return qs


#  ------------------------------------------------------------


@admin.register(InfoPacketSet)
class InfoPacketSetAdmin(CustomModelAdmin):
    filter_horizontal = ['infopackets']
    list_display = ['id', 'title', 'get_infopackets']
    list_editable = ['title']
    search_fields = ['title']

    @admin.display(description="InfoPackets")
    def get_infopackets(self, obj):
        return mark_safe(
            "<br>".join([f"✧ {obj.title}" for obj in obj.infopackets.all()]))


#  ------------------------------------------------------------
