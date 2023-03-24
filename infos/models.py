from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import (
    CASCADE, PROTECT, TextChoices, Model, CharField, ForeignKey as FK,
    IntegerField, TextField, ManyToManyField as M2M, URLField,
)
from django.db.models.functions import Collate

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

# TODO wszystkie pakiety łącznie, żeby można było je łączyć w meta-pakiety,
#  niezaleznie od kind; również pakiety z info mogą iść do dialogów czyichś.
# TODO MapPacket -> InfoPacket, bo po co to rozróżniać

class InfoPacket(Model):

    class InfoPacketKind(TextChoices):
        KNOWLEDGE = "1. KNOWLEDGE", "KNOWLEDGE"
        BIOGRAPHY = "2. BIOGRAPHY", "BIOGRAPHY"
        DIALOGUE = "3. DIALOGUE", "DIALOGUE"

    infopacketkind = CharField(
        max_length=15, choices=InfoPacketKind.choices,
        default=InfoPacketKind.KNOWLEDGE)
    title = CharField(max_length=100)
    text = TextField() # TODO from ckeditor.fields import RichTextField
    references = M2M(to=Reference, related_name='infopackets', blank=True)

    author = FK(
        'characters.Character', related_name='infopacketsauthored', on_delete=PROTECT,
        null=True, blank=True)
    informees = M2M('characters.Character', related_name='infopackets', blank=True)

    # skills = M2M(to=Skill, related_name='infopackets')
    ininfopackets = M2M(
        'self', related_name='infopackets', blank=True,
        through='InfoPacketPosition')
    pictureversions = GenericRelation(PictureVersion)


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


"""
Działanie:
Docelowo 1-3 poziomy InfoPacket, zależnie od pakietu:
    1. pakiet-kubełek: pakiet na inne pakiety, np. Wierzenia Tirsenów
        - może mieć absolutne minimum tekstu np. "Spis bóstw i mitów Tirsenów"

        2. pakiet-duzy: taki, który zawiera trochę informacji
            - odpowiada InfoPacket z Hyllemath 1.0
            - składa się z 2 lub więcej pakietów-małych

            3. pakiet-mały: najmniejsza cząstka informacyjna
                - odpowiada akapitom lub podrozdziałom InfoPacket z Hyllemath 1.0
                - stylizowany jako podrozdziały z tytułem (trzeba nadać zawsze)

Przy tym robić tak, że niezależnie czy są 1, 2 czy 3 poziomy, pierwszy jaki
wystąpi w hierarchii poziomów jest stylizowany zawsze tak samo, drugi też zawsze
jako drugi, i trzeci ma swój styl, jeśli jest.
W HTML mogłoby to odpowiadać koncepcyjnie I - <h1>, II - <h2>, III - <h3>
przy czym czasem to pakiet-mały będzie I - <h1>.
Oczywiście dać im inny style niż <h1> itp.
"""