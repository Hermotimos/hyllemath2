from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, TextChoices, Model, Manager,
    CharField, ForeignKey as FK, DateTimeField, PositiveIntegerField,
    IntegerField, TextField, BooleanField, ManyToManyField as M2M
)
from django.core.validators import MinValueValidator, MaxValueValidator

from resources.models import Picture
from myproject.utils_models import Tag
from users.models import User

# TODO: add absolute_url when applicable


#  ------------------------------------------------------------

# Tags


class FirstNameTag(Tag):
    user = FK(
        User, related_name='firstnametags',
        null=True, blank=True, on_delete=CASCADE)


class FamilyNameTag(Tag):
    user = FK(
        User, related_name='familynametags',
        null=True, blank=True, on_delete=CASCADE)



class CharacterVersionTag(Tag):
    user = FK(
        User, related_name='characterversiontags',
        null=True, blank=True, on_delete=CASCADE)


#  ------------------------------------------------------------


class FirstNameGroup(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class FirstName(Model):

    class Gender(TextChoices):
        MALE = "MALE", "MALE"
        FEMALE = "FEMALE", "FEMALE"
        UNISEX = "UNISEX", "UNISEX"
        NONE = "NONE", "NONE"

    gender = CharField(max_length=6, choices=Gender.choices, default=Gender.MALE)
    firstnamegroup = FK(FirstNameGroup, related_name='firstnames', on_delete=PROTECT)
    origin = FK(
        "self", related_name='originatedfirstnames',
        null=True, blank=True, on_delete=PROTECT)
    nominative = CharField(max_length=50, unique=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000)
    tags = M2M(FirstNameTag, blank=True)

    class Meta:
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


#  ------------------------------------------------------------


class FamilyNameGroup(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000)

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
    description = TextField(max_length=10000)
    tags = M2M(FamilyNameTag,  related_name='familynames', blank=True)

    class Meta:
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


#  ------------------------------------------------------------


class Character(Model):
    user = FK("users.User", related_name='characters', on_delete=CASCADE)
    relationships = M2M(
        'CharacterVersion', through='Relationship',
        related_name='known_by_characters', blank=True)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user"]

    def __str__(self):
        try:
            # Get Character's version with greatest CharacterVersionKind,
            # the order being "1. DEAD" > "2. MAIN" > "3. PAST" >  "4. PARTIAL"
            fullname, versionkind = CharacterVersion.objects.filter(
                character__id=self.id
            ).order_by(
                "versionkind"
            ).values_list(
                'fullname', 'versionkind'
            ).first()
            return f"{self.user.username}: {fullname} ({versionkind})"
        except:
            return f"{self.user.username}: No CharacterVersion"



class CharacterVersion(Model):

    class CharacterVersionKind(TextChoices):
        DEAD = "1. DEAD", "DEAD"
        MAIN = "2. MAIN", "MAIN"
        PAST = "3. PAST", "PAST"
        PARTIAL = "4. PARTIAL", "PARTIAL"

    character = FK(Character, related_name='characterversions', on_delete=PROTECT)
    versionkind = CharField(max_length=10, choices=CharacterVersionKind.choices, default=CharacterVersionKind.MAIN)
    picture = FK(Picture, related_name='characterversions', on_delete=PROTECT)
    isalive = BooleanField(default=True)
    isalterego = BooleanField(default=False)

    firstname = FK(FirstName, on_delete=PROTECT, null=True, blank=True)
    familyname = FK(FamilyName, on_delete=PROTECT, null=True, blank=True)
    nickname = CharField(max_length=50, null=True, blank=True)
    originname = CharField(max_length=50, null=True, blank=True)
    fullname = CharField(max_length=100)

    description = TextField(max_length=10000, null=True)
    strength = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    dexterity = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    endurance = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    power = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    experience = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])

    tags = M2M(CharacterVersionTag, related_name='characterversions', blank=True)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fullname"]

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


