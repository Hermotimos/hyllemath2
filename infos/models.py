from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, SET_DEFAULT, TextChoices, Model, Manager, F,
    CharField, ForeignKey as FK, DateTimeField, PositiveIntegerField,
    IntegerField, PositiveSmallIntegerField, TextField, BooleanField,
    ManyToManyField as M2M, Index, URLField,
)
from django.db.models.functions import Collate
from django.utils.html import format_html

from myproject.utils_models import Tag, get_gamemaster, min_max
from resources.models import Picture
from users.models import User


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

# TODO wszystkie pakiety łącznie, żeby można było je łączyć w meta-pakiety,
#  niezaleznie od kind; również pakiety z info mogą iść do dialogów czyichś.
# TODO MapPacket -> InfoPacket, bo po co to rozróżniać

class InfoPacket(Model):

    class InfoPacketKind(TextChoices):
        KNOWLEDGE = "1. KNOWLEDGE", "KNOWLEDGE"
        BIOGRAPHY = "2. BIOGRAPHY", "BIOGRAPHY"
        DIALOGUE = "3. DIALOGUE", "DIALOGUE"

    title = CharField(max_length=100)
    text = TextField() # TODO from ckeditor.fields import RichTextField
    infopacketkind = CharField(
        max_length=15, choices=InfoPacketKind.choices,
        default=InfoPacketKind.KNOWLEDGE)
    author = FK(
        'characters.Character', related_name='infopacketsauthored', on_delete=PROTECT,
        null=True, blank=True)
    informees = M2M('characters.Character', related_name='infopackets', blank=True)
    references = M2M(to=Reference, related_name='infopackets', blank=True)

    # skills = M2M(to=Skill, related_name='infopackets')
    ininfopackets = M2M(
        'self', related_name='infopackets', blank=True,
        through='InfoPacketPosition')
    # TODO PicturePosition wzorem InfoPacketPosition jeśli zadziała
    # picture_sets = M2M(
    #     Picture, related_name='infopackets', blank=True,
    #     through='Position')

    class Meta:
        ordering = [Collate('title', 'pl-PL-x-icu'), 'infopacketkind']


class InfoPacketPosition(Model):
    containing_infopacket = FK(
        InfoPacket, related_name='contained_infopackets', on_delete=CASCADE)
    contained_infopacket = FK(
        InfoPacket, related_name='containing_infopackets', on_delete=CASCADE)
    orderdum = IntegerField()

    class Meta:
        ordering = [Collate('containing_infopacket__title', 'pl-PL-x-icu')]
        unique_together = ['containing_infopacket', 'contained_infopacket']

    def __str__(self):
        return f"{self.containing_infopacket} -> {self.contained_infopacket}"


#  ------------------------------------------------------------

