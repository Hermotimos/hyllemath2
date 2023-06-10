from django.contrib import admin
from django.utils.safestring import mark_safe

from infos.models import (
    InfoItem, InfoItemVersion, InfoPacket, InfoPacketKind, InfoPacketSet,
    Reference,
)
from myproject.utils_admin import CustomModelAdmin


@admin.register(Reference)
class ReferenceAdmin(CustomModelAdmin):
    list_display = ['id', 'title', 'description', 'url']
    list_editable = ['title', 'description', 'url']
    search_fields = ['title', 'description', 'url']


#  ------------------------------------------------------------


@admin.register(InfoItem)
class InfoItemAdmin(CustomModelAdmin):
    list_display = [
        'id', 'enigmalevel', 'title', 'isrestricted',
        '_createdby', '_createdat'
    ]
    list_editable = ['enigmalevel', 'title', 'isrestricted',]
    list_filter = ['enigmalevel', 'isrestricted', '_createdby']
    search_fields = ['title']


#  ------------------------------------------------------------


@admin.register(InfoItemVersion)
class InfoItemVersionAdmin(CustomModelAdmin):
    list_display = ['id', 'infoitem', 'versionkind', 'text']
    list_editable = ['infoitem', 'versionkind', 'text']
    list_filter = ['infoitem__enigmalevel', 'versionkind']
    search_fields = ['text']


#  ------------------------------------------------------------


@admin.register(InfoPacketKind)
class InfoPacketKindAdmin(CustomModelAdmin):
    list_display = ['id', 'name', 'locationordering', 'characterordering']
    list_editable = ['name', 'locationordering', 'characterordering']


#  ------------------------------------------------------------


@admin.register(InfoPacket)
class InfoPacketAdmin(CustomModelAdmin):
    filter_horizontal = ['infopacketkinds', 'infoitems', 'references']
    list_display = ['id', 'title', 'get_infopacketkinds', 'get_infoitems']
    list_editable = ['title']
    search_fields = ['title']

    @admin.display(description="InfoPacketKinds")
    def get_infopacketkinds(self, obj):
        return mark_safe(
            "<br>".join([f"✧ {obj.name}" for obj in obj.infopacketkinds.all()]))

    @admin.display(description="InfoItems")
    def get_infoitems(self, obj):
        return mark_safe(
            "<br>".join([f"✧ {obj.title}" for obj in obj.infoitems.all()]))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('infoitems', 'infopacketkinds')
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
