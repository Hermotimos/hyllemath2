from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.functions import Collate
from django.db.models import (
    CASCADE, PROTECT, TextChoices, Model, CharField, ForeignKey as FK,
    IntegerField, TextField, ManyToManyField as M2M, URLField, DateTimeField,
    Manager, SET_NULL, Q, CheckConstraint, Count, UniqueConstraint,
    BooleanField,
)
from django.utils.safestring import mark_safe

from resources.models import PicturePosition, Picture


#  ------------------------------------------------------------


class Reference(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField()
    url = URLField(max_length=500)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


#  ------------------------------------------------------------


class InfoItemManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('infoitemversions')
        qs = qs.select_related('_createdby')
        return qs


class InfoItem(Model):
    objects = InfoItemManager()

    class EnigmaLevel(TextChoices):
        _0 = "0", "0"
        _1 = "1", "1"
        _2 = "2", "2"
        _3 = "3", "3"

    enigmalevel = CharField(
        max_length=1, choices=EnigmaLevel.choices, default=EnigmaLevel._0)
    title = CharField(max_length=100)
    # TODO isrestricted=True should prevent from adding non-GMs to knowledges
    # in InfoItemVersion's of this InfoItem
    isrestricted = BooleanField(default=True)
    _createdat = DateTimeField(auto_now_add=True)
    _createdby = FK(
        'characters.Character', related_name='infoitemscreated',
        on_delete=PROTECT, blank=True, null=True)

    class Meta:
        ordering = ['enigmalevel', 'title']

    def __str__(self):
        enigmalevel = self.enigmalevel.replace("_", "")
        return f"[{enigmalevel}] {self.title}"


#  ------------------------------------------------------------


class InfoItemVersionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'infoitem',
        )
        return qs


class InfoItemVersion(Model):
    objects = InfoItemVersionManager()

    class InfoItemVersionKind(TextChoices):
        MAIN = "1. MAIN", "MAIN"
        PARTIAL = "2. PARTIAL", "PARTIAL"
        PAST = "3. PAST", "PAST"
        BYPLAYER = "4. BYPLAYER", "BYPLAYER"

    infoitem = FK(InfoItem, related_name='infoitemversions', on_delete=PROTECT)
    versionkind = CharField(
        max_length=15, choices=InfoItemVersionKind.choices,
        default=InfoItemVersionKind.MAIN)
    versioncomment = TextField(max_length=1000, blank=True, null=True)

    text = TextField() # TODO from ckeditor.fields import RichTextField
    references = M2M(Reference, related_name='infoitems', blank=True)
    picturepositions = GenericRelation('resources.PicturePosition')
    knowledges = GenericRelation('characters.Knowledge')
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["infoitem", "versionkind"]
        constraints = [
            UniqueConstraint(
                fields=['infoitem', 'versionkind'],
                name='unique_infoitemversion_infoitem_versionkind'),
            UniqueConstraint(
                fields=['infoitem'],
                condition=Q(versionkind="1. MAIN"),
                name='unique_infoitemversion_main')
        ]

    def __str__(self):
        return f"{self.infoitem.title} {self.versionkind[3:]}"


#  ------------------------------------------------------------


class InfoPacketKind(Model):
    name = CharField(max_length=100, unique=True)
    description = TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InfoPacket(Model):
    infopacketkind = FK(InfoPacketKind, on_delete=PROTECT)
    title = CharField(max_length=100)
    # picture = FK(
    #     Picture, related_name='infopackets', on_delete=PROTECT,
    #     blank=True, null=True)  # TODO in future add a pic for each packet
    infoitems = M2M(InfoItem, through='InfoItemPosition', related_name='infopackets')

    class Meta:
        ordering = ['infopacketkind', Collate('title', 'pl-PL-x-icu')]

    def __str__(self):
        return f"{self.title} [{self.infopacketkind}]"


#  ------------------------------------------------------------


class InfoItemPosition(Model):
    """A model for positioning InfoItem-s within InfoPacket-s."""

    infoitem = FK(InfoItem, related_name='positionsininfopackets', on_delete=CASCADE)
    infopacket = FK(InfoPacket, related_name='infoitempositions', on_delete=CASCADE)
    position = IntegerField(default=1)

    class Meta:
        ordering = ['infopacket', 'position']
        unique_together = ['infoitem', 'infopacket']

    def __str__(self):
        return f"{self.infopacket} -> {self.infoitem}"


#  ------------------------------------------------------------


class InfoPacketSetManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related(
            'infopackets',
        )
        return qs


class InfoPacketSet(Model):
    objects = InfoPacketSetManager()

    title = CharField(max_length=100, unique=True)
    infopackets = M2M(InfoPacket, related_name='infopacketsets')
    # skills = M2M(
    #     Skill, through='InfoPacketSetPosition', related_name='infopacketsets')

    class Meta:
        ordering = [Collate('title', 'pl-PL-x-icu')]

    def __str__(self):
        return self.title


#  ------------------------------------------------------------

# TODO: When rules.Skill is ready decide if M2M field goes here or there.
# This is for: Skill=History, InfoPacketSets=[History of Kalshad, History of Hyllemath, ...]

# class InfoPacketSetPosition(Model):
#     """A model for positioning InfoPacketset-s within Skill-s."""

#     infopacketset = FK(InfoItem, related_name='positionsiniskills', on_delete=CASCADE)
#     skill = FK(InfoPacket, related_name='infopacketsetpositions', on_delete=CASCADE)
#     position = IntegerField(default=1)

#     class Meta:
#         ordering = ['skill', 'position']
#         unique_together = ['infopacketset', 'skill']

#     def __str__(self):
#         return f"{self.skill}: [{self.position}] {self.infopacketset}"
