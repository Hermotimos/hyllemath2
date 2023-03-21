from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, SET_DEFAULT, TextChoices, Model, Manager, F,
    CharField, ForeignKey as FK, DateTimeField, PositiveIntegerField,
    IntegerField, PositiveSmallIntegerField, TextField, BooleanField,
    ManyToManyField as M2M, Index
)
from django.db.models.functions import Collate
from django.utils.html import format_html

from resources.models import Picture
from myproject.utils_models import Tag, get_gamemaster, min_max
from users.models import User


#  ------------------------------------------------------------


class FirstNameTag(Tag):
    # add unique constraint as this is for GM use only
    title = CharField(max_length=50, unique=True)


class FamilyNameTag(Tag):
    # add unique constraint as this is for GM use only
    title = CharField(max_length=50, unique=True)


class CharacterVersionTag(Tag):
    user = FK(User, related_name='characterversiontags', on_delete=CASCADE)

    class Meta:
        ordering = [
            F('user').asc(nulls_first=True),
            'title',
        ]
        unique_together = ['title', 'user']


#  ------------------------------------------------------------


class FirstNameGroupManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('parentgroup')
        return qs


class FirstNameGroup(Model):
    objects = FirstNameGroupManager()

    parentgroup = FK(
        'self', related_name='firstnamegroups', on_delete=PROTECT,
        blank=True, null=True)
    title = CharField(max_length=100)
    description = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["title"]
        unique_together = [("title", "parentgroup")]

    def __str__(self):
        parentgroup = f" [{self.parentgroup.title}]" if self.parentgroup else ""
        return  format_html(
            f'<strong style="color: #7fff00;">{self.title}</strong> {parentgroup}')



class FirstNameManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('firstnamegroup__parentgroup')
        return qs



class FirstName(Model):
    objects = FirstNameManager()

    class Gender(TextChoices):
        MALE = "MALE", "MALE"
        FEMALE = "FEMALE", "FEMALE"
        UNISEX = "UNISEX", "UNISEX"
        NONE = "NONE", "NONE"

    firstnamegroup = FK(FirstNameGroup, related_name='firstnames', on_delete=PROTECT)
    gender = CharField(max_length=6, choices=Gender.choices, default=Gender.MALE)
    isarchaic = BooleanField(default=False)
    nominative = CharField(max_length=50, unique=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    origin = FK(
        "self", related_name='originatedfirstnames',
        blank=True, null=True, on_delete=PROTECT)
    equivalents = M2M('self', symmetrical=True, blank=True)
    meaning = TextField(max_length=10000, blank=True, null=True)
    description = TextField(max_length=10000, blank=True, null=True)
    tags = M2M(FirstNameTag, related_name='firstnames', blank=True)
    _comment = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = [Collate('nominative', 'pl-PL-x-icu')]

    def __str__(self):
        return self.nominative

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Call related objects' save() methods to reevaluate fullname
        for characterversion in self.characterversions.all():
            characterversion.save()


#  ------------------------------------------------------------


class FamilyNameGroup(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class FamilyName(Model):
    familynamegroup = FK(
        FamilyNameGroup, related_name='familynames', on_delete=PROTECT)
    origin = FK(
        "self", related_name='originatedfamilynames',
        blank=True, null=True, on_delete=SET_NULL)
    nominative = CharField(max_length=50, unique=True)
    nominative_pl = CharField(max_length=50, blank=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    genitive_pl = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000, blank=True, null=True)
    tags = M2M(FamilyNameTag, related_name='familynames', blank=True)
    _comment = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Call related objects' save() to reevaluate CharacterVersion.fullname
        for characterversion in self.characterversions.all():
            characterversion.save()


#  ------------------------------------------------------------


class CharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('user')
        return qs


class Character(Model):
    objects = CharacterManager()

    user = FK(User, related_name='characters', default=get_gamemaster, on_delete=CASCADE)
    strength = IntegerField(default=9, validators=min_max(1,20), blank=True, null=True)
    dexterity = IntegerField(default=9, validators=min_max(1,20), blank=True, null=True)
    endurance = IntegerField(default=9, validators=min_max(1,20), blank=True, null=True)
    power = IntegerField(default=1, validators=min_max(1,20), blank=True, null=True)
    experience = PositiveSmallIntegerField(blank=True, null=True)
    _mainversionname = CharField(max_length=150, blank=True, null=True)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__is_superuser", "_mainversionname"]

    def __str__(self):
        if self._mainversionname:
            return str(self._mainversionname)
        return f"{self.user.username} - {self.id}"


class CharacterKnownCharacterVersion(Character):
    """A proxy class for a separate AdminModel."""

    class Meta:
        proxy = True


class CharacterKnownLocationVersion(Character):
    """A proxy class for a separate AdminModel."""

    class Meta:
        proxy = True


#  ------------------------------------------------------------


class KnowledgeManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('character__user')
        return qs


class Knowledge(Model):
    objects = KnowledgeManager()

    # technical fields of Generic relations
    content_type = FK(ContentType, related_name='characters', on_delete=CASCADE)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    character = FK(Character, related_name='knowledges', on_delete=PROTECT)
    isdirect = BooleanField(default=False)
    identifiedwith = ArrayField(PositiveIntegerField(), blank=True, null=True)
    # TODO identifiedwith is for overriding DISTINCT ON (character_id, isalterego) in player's view

    class Meta:
        indexes = [
            Index(fields=["content_type", "object_id"]),
            # Index(fields=["character"]),  # TODO sprawdzić czy już nie ma z defaultu
        ]

    def __str__(self):
        return f"{self.character} -> {self.content_object}"


#  ------------------------------------------------------------


class CharacterVersionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'picture', 'firstname', 'familyname', '_createdby',
        )
        return qs


class CharacterVersion(Model):
    objects = CharacterVersionManager()

    class CharacterVersionKind(TextChoices):
        DEAD = "1. DEAD", "DEAD"
        MAIN = "2. MAIN", "MAIN"
        CHANGED = "3. CHANGED", "CHANGED"
        PARTIAL = "4. PARTIAL", "PARTIAL"
        PAST = "5. PAST", "PAST"
        BYPLAYER = "6. BYPLAYER", "BYPLAYER"

    character = FK(
        Character, related_name='characterversions', on_delete=PROTECT,
        blank=True, null=True)  # for player-created ones
    versionkind = CharField(
        max_length=15, choices=CharacterVersionKind.choices,
        default=CharacterVersionKind.MAIN)
    isalterego = BooleanField(default=False)

    # versioned stuff
    isalive = BooleanField(default=True)
    picture = FK(
        Picture, related_name='characterversions', on_delete=PROTECT,
        blank=True, null=True)  # for player-created ones
    firstname = FK(
        FirstName, related_name='characterversions', on_delete=PROTECT,
        blank=True, null=True)
    familyname = FK(
        FamilyName, related_name='characterversions', on_delete=PROTECT,
        blank=True, null=True)
    nickname = CharField(max_length=50, blank=True, null=True)
    originname = CharField(max_length=50, blank=True, null=True)
    fullname = CharField(max_length=200)    # redundant, handier than property
    description = TextField(max_length=10000, blank=True, null=True)

    knowledges = GenericRelation(Knowledge)

    # frequentedlocations = M2M(to=Location, related_name='characters', blank=True)
    # biopackets = M2M(to=BiographyPacket, related_name='characters', blank=True)
    # dialoguepackets = M2M(to=DialoguePacket, related_name='characters', blank=True)
    # subprofessions = M2M(to=SubProfession, related_name='characters', blank=True)
    # skilllevels = M2M(
    #     to=SkillLevel,
    #     through='Acquisition',
    #     related_name='acquiring_characters',
    #     blank=True)

    tags = M2M(CharacterVersionTag, related_name='characterversions', blank=True)
    _createdby = FK(
        Character, related_name='characterversionscreated', on_delete=SET_NULL,
        blank=True, null=True)
    _createdat = DateTimeField(auto_now_add=True)
    _comment = TextField(max_length=1000, blank=True, null=True)

    class Meta:
        ordering = [Collate('fullname', 'pl-PL-x-icu'), "versionkind"]
        unique_together = [
            ['character', 'picture', 'versionkind', 'fullname'],
        ]

    def __str__(self):
        return f"{self.fullname} ({self.versionkind})"

    def save(self, *args, **kwargs):
        # reevaluate fullname on each save;
        # called by FirstName.save() and FamilyName.save()
        firstname, familyname, nickname, originname = (
            getattr(self.firstname, 'nominative', ""),
            getattr(self.familyname, 'nominative', ""),
            self.nickname or "",
            self.originname or "",
        )
        fullname = f"{firstname} {familyname} {nickname} {originname}"
        self.fullname = fullname.replace('  ', ' ').strip()

        # When updating MAIN version, update related model's _mainversionname
        if self.versionkind == '2. MAIN':
            self.character._mainversionname = self.fullname
            self.character.save()

        super().save(*args, **kwargs)

    # TODO
    # def get_absolute_url(self):
    #     return settings.BASE_URL + reverse('prosoponomikon:character', kwargs={'character_id' : self.id})


#  ------------------------------------------------------------


# TODO
#   1) zrobić logikę widoków, gdzie Prosoponomikon prezentuje Graczowi tę
#      "największą" CharacterVersion należąca do danego Character:
#           - weź wszystkie znane CharacterVersion,
#           - weź ich Character i zrób listę DISTINCT ON (character_id, isalterego)
#               (czyli gdy nie chodzi o zakres znajomości, a o "drugą tożsamość")
#           - z każdego Character weź te CharacterVersion, która Gracz zna
#           - z nich weź "największą": DEAD > MAIN > CHANGED > PARTIAL > PAST > BYPLAYER
#           - i tę zaprezentuj w widoku listy (Prosoponomikon main)
#   2) dla widoku detail prezentować wszystkie wersje, które się różnią:
#      description, picture (inne różnice to updaty wiedzy: imię itp.)


#  ------------------------------------------------------------

