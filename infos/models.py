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


class InfoItem(Model):
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
                fields=['infoitem', 'text', 'versionkind'],
                name='unique_infoitemversion_infoitem_versionkind'),
            UniqueConstraint(
                fields=['infoitem'],
                condition=Q(versionkind="1. MAIN"),
                name='unique_infoitemversion_main')
        ]

    def __str__(self):
        return f"{self.infoitem.title} {self.versionkind[3:]}"


#  ------------------------------------------------------------


class InfoPacket(Model):
    INFO_PACKET_KINDS = [
        # temp for data migration - TODO: change to specific
        ("TEMP-0-GENERAL",   "TEMP-0-GENERAL"),
        # characters
        ("CHA-1-BIOGRAPHY",  "CHA-1-BIOGRAPHY"),
        ("CHA-2-SECRETS",    "CHA-2-SECRETS"),
        # locations
        ("LOC-1-GEOGRAPHY",  "LOC-1-GEOGRAPHY"),
        ("LOC-2-BIOLOGY",    "LOC-2-BIOLOGY"),
        ("LOC-3-ECONOMICS",  "LOC-3-ECONOMICS"),
    ]
    infopacketkind = CharField(
        max_length=100, choices=INFO_PACKET_KINDS, default="TEMP-0-GENERAL")
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
    """A model for positioning InfoItem-s within InfoPacket's."""

    infoitem = FK(InfoItem, related_name='positionsininfopackets', on_delete=CASCADE)
    infopacket = FK(InfoPacket, related_name='infoitempositions', on_delete=CASCADE)
    position = IntegerField(default=1)

    class Meta:
        ordering = ['infopacket', 'position']
        unique_together = ['infopacket', 'infoitem']

    def __str__(self):
        return f"{self.infopacket} -> {self.infoitem}"


#  ------------------------------------------------------------


class InfoPacketSet(Model):
    title = CharField(max_length=100)
    infopackets = M2M(InfoPacket, related_name='infopacketsets')
    # skills = M2M(to=Skill, related_name='infopacketsets')

    class Meta:
        ordering = [Collate('title', 'pl-PL-x-icu')]

    def __str__(self):
        return self.title
