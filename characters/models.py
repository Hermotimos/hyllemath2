from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, SET_DEFAULT, TextChoices, Model, Manager, F,
    CharField, ForeignKey as FK, DateTimeField, PositiveIntegerField,
    IntegerField, PositiveSmallIntegerField, TextField, BooleanField, ManyToManyField as M2M
)

from resources.models import Picture
from myproject.utils_models import Tag, get_gamemaster, min_max_validators
from users.models import User

# TODO: add absolute_url when applicable


#  ------------------------------------------------------------

# Tags


class FirstNameTag(Tag):
    title = CharField(max_length=50, unique=True)


class FamilyNameTag(Tag):
    title = CharField(max_length=50, unique=True)


class CharacterVersionTag(Tag):
    user = FK(
        User, related_name='characterversiontags',
        null=True, blank=True, on_delete=CASCADE)

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
        return self.title + parentgroup



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
        null=True, blank=True, on_delete=PROTECT)
    equivalents = M2M('self', symmetrical=True, blank=True)
    meaning = TextField(max_length=10000, blank=True, null=True)
    description = TextField(max_length=10000, blank=True, null=True)
    tags = M2M(FirstNameTag, blank=True)
    comments = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


#  ------------------------------------------------------------


class FamilyNameGroup(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class FamilyName(Model):
    familynamegroup = FK(FamilyNameGroup, related_name='familynames', on_delete=PROTECT)
    origin = FK(
        "self", related_name='originatedfamilynames',
        null=True, blank=True, on_delete=SET_NULL)
    nominative = CharField(max_length=50, unique=True)
    nominative_pl = CharField(max_length=50, blank=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    genitive_pl = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000, blank=True, null=True)
    tags = M2M(FamilyNameTag,  related_name='familynames', blank=True)
    comments = TextField(max_length=10000, blank=True, null=True)

    class Meta:
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


#  ------------------------------------------------------------


class CharacterManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('user')
        return qs


class Character(Model):
    objects = CharacterManager()

    user = FK(User, related_name='characters', default=get_gamemaster, on_delete=CASCADE)
    relationships = M2M(
        'CharacterVersion', through='Relationship',
        related_name='known_by_characters', blank=True)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user__is_superuser", "user__username"]

    def __str__(self):
        return f"{self.user.username} - {self.id}"


class CharacterVersionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
             'picture', 'firstname', 'familyname', '_createdby').prefetch_related('character__user__characters')
        return qs


class CharacterVersion(Model):
    objects = CharacterVersionManager()

    class CharacterVersionKind(TextChoices):
        DEAD = "1. DEAD", "DEAD"
        MAIN = "2. MAIN", "MAIN"
        CHANGED = "3. CHANGED", "CHANGED"
        PARTIAL = "4. PARTIAL", "PARTIAL"
        PAST = "5. PAST", "PAST"

    character = FK(
        Character, related_name='characterversions', on_delete=PROTECT,
        null=True, blank=True)  # for player-created ones
    picture = FK(
        Picture, related_name='characterversions', on_delete=PROTECT,
        null=True, blank=True)  # for player-created ones
    versionkind = CharField(
        max_length=10, choices=CharacterVersionKind.choices,
        default=CharacterVersionKind.MAIN)
    isalive = BooleanField(default=True)
    isalterego = BooleanField(default=False)

    firstname = FK(FirstName, on_delete=PROTECT, null=True, blank=True)
    familyname = FK(FamilyName, on_delete=PROTECT, null=True, blank=True)
    nickname = CharField(max_length=50, null=True, blank=True)
    originname = CharField(max_length=50, null=True, blank=True)
    fullname = CharField(max_length=100)

    strength = IntegerField(null=True, default=9, validators=min_max_validators(1,20))
    dexterity = IntegerField(null=True, default=9, validators=min_max_validators(1,20))
    endurance = IntegerField(null=True, default=9, validators=min_max_validators(1,20))
    power = IntegerField(null=True, default=0, validators=min_max_validators(0,20))
    experience = PositiveSmallIntegerField(null=True)
    description = TextField(max_length=10000, blank=True, null=True)

    tags = M2M(CharacterVersionTag, related_name='characterversions', blank=True)
    _createdby = FK(
        User, related_name='createdcharacterversionss', on_delete=SET_NULL,
        null=True, blank=True)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fullname"]
        unique_together = [
            ['character', 'picture', 'versionkind', 'fullname'],
        ]

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        firstname, familyname, nickname, originname = (
            getattr(self.firstname, 'nominative', ""),
            getattr(self.familyname, 'nominative', ""),
            self.nickname or "",
            self.originname or "",
        )
        fullname = f"{firstname} {familyname} {nickname} {originname}"
        self.fullname = fullname.replace('  ', ' ').strip()
        super().save(*args, **kwargs)


class Relationship(Model):
    character = FK(Character, on_delete=PROTECT)
    characterversion = FK(CharacterVersion, on_delete=PROTECT)
    isdirect = BooleanField(default=False)
    identifiedwith = ArrayField(PositiveIntegerField(), blank=True, null=True)

    class Meta:
        unique_together = ['character', 'characterversion']

    def __str__(self):
        return f"{self.character} -> ({self.characterversion.versionkind}) -> {self.characterversion}"


#  ------------------------------------------------------------


