from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.functions import Collate
from django.db.models import (
    CASCADE, PROTECT, TextChoices, Model, CharField, ForeignKey as FK,
    IntegerField, TextField, ManyToManyField as M2M, URLField, DateTimeField,
    Manager, SET_NULL, Q, CheckConstraint, Count, UniqueConstraint,
)
from django.utils.safestring import mark_safe

from resources.models import PictureVersion

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

    enigmalevel = CharField(max_length=1, choices=EnigmaLevel.choices)
    title = CharField(max_length=100)
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

    text = TextField() # TODO from ckeditor.fields import RichTextField
    pictureversions = GenericRelation(PictureVersion)
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


class InfoPacketKind(Model):
    name = CharField(max_length=50) # ex. LOC-GEOGRAPHY, LOC-BIOLOGY, LOC-ECONOMICS, CHA-BIOGRAPHY, CHA-SECRETS
    locationordering = IntegerField(blank=True, null=True)
    characterordering = IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["locationordering", "characterordering", "name"]

    def __str__(self):
        return self.name


class InfoPacket(Model):
    infopacketkinds = M2M(InfoPacketKind, related_name='infopackets')
    title = CharField(max_length=100)
    infoitems = M2M(
        InfoItem, related_name='infopackets',
        help_text=mark_safe(
            '<span style="color:red;font-size:1.2rem;">'
            '❖ InfoItems of the same Enigma Level!</span><br>'))
    references = M2M(Reference, related_name='infopackets', blank=True)

    class Meta:
        ordering = [Collate('title', 'pl-PL-x-icu')]

    def __str__(self):
        return self.title


#  ------------------------------------------------------------


class InfoPacketSet(Model):
    title = CharField(max_length=100)
    infopackets = M2M(InfoPacket, related_name='infopacketsets')
    # skills = M2M(to=Skill, related_name='infopacketsets')

    class Meta:
        ordering = [Collate('title', 'pl-PL-x-icu')]

    def __str__(self):
        return self.title
