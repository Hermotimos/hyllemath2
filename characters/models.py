from django.db.models import (
    CASCADE, PROTECT, SET_NULL, TextChoices, Model,
    AutoField, CharField, ForeignKey, Index, DateTimeField,
    IntegerField, TextField, BooleanField, ManyToManyField
)
from django.core.validators import MinValueValidator, MaxValueValidator

from resources.models import Tag, Picture


# TODO: check if Django uses indexes on "id" fields even if they aren"t mentioned in Meta - speed tests
# TODO: add ordering
# TODO: add absolute_url when applicable


#  -------------------------------------------------------------------------------


class FirstNameGroup(Model):
    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000)

    class Meta:
        managed = False
        db_table = '"cha"."firstnamegroup"'
        ordering = ["title"]

    def __str__(self):
        return self.title


class FirstName(Model):

    class Gender(TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        UNISEX = "UNISEX", "Unisex"
        NONE = "NONE", "None"

    id = AutoField(primary_key=True)
    firstnamegroup = ForeignKey(FirstNameGroup, related_name='firstnames', on_delete=PROTECT)
    origin = ForeignKey("self", related_name='originatedfirstnames', null=True, blank=True, on_delete=PROTECT)
    gender = CharField(max_length=6, choices=Gender.choices, default=Gender.MALE)
    nominative = CharField(max_length=50, unique=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000)
    _tags = ManyToManyField(Tag, through="FirstNameToTagLink", blank=True)

    # TODO: M2M Field tags = M2MField(FirstNameTag, ...) to reflect links instead of separate table - this should work

    class Meta:
        managed = False
        db_table = '"cha"."firstname"'
        indexes = [
            Index(fields=["firstnamegroup"]),
            Index(fields=["origin"]),
        ]
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


class FirstNameToTagLink(Model):
    id = AutoField(primary_key=True)
    firstname = ForeignKey(FirstName, on_delete=CASCADE)
    tag = ForeignKey(Tag, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."firstnametotaglink"'


#  -------------------------------------------------------------------------------


class FamilyNameGroup(Model):
    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000)

    class Meta:
        managed = False
        db_table = '"cha"."familynamegroup"'
        ordering = ["title"]

    def __str__(self):
        return self.title


class FamilyName(Model):
    id = AutoField(primary_key=True)
    familynamegroup = ForeignKey(FamilyNameGroup, related_name='familynames', on_delete=PROTECT)
    origin = ForeignKey("self", related_name='originatedfamilynames', null=True, blank=True, on_delete=SET_NULL)
    nominative = CharField(max_length=50, unique=True)
    nominative_pl = CharField(max_length=50, blank=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    genitive_pl = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000)
    _tags = ManyToManyField(Tag, through="FamilyNameToTagLink", blank=True)

    class Meta:
        managed = False
        db_table = '"cha"."familyname"'
        indexes = [
            Index(fields=["familynamegroup"]),
            Index(fields=["origin"]),
        ]
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


class FamilyNameToTagLink(Model):
    id = AutoField(primary_key=True)
    familyname = ForeignKey(FamilyName, on_delete=CASCADE)
    tag = ForeignKey(Tag, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."familynametotaglink"'


#  -------------------------------------------------------------------------------


class Character(Model):
    id = AutoField(primary_key=True)
    user = ForeignKey("users.User", related_name='characters', on_delete=CASCADE)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"cha"."character"'
        ordering = ["user"]

    def __str__(self):
        main_version = ""     # TODO
        return f"[{self.user.username}] - {main_version}"


class CharacterVersion(Model):

    class CharacterVersionKind(TextChoices):
        DEAD = "DEAD", "Dead"
        MAIN = "MAIN", "Main"
        PAST = "PAST", "Past"
        PARTIAL = "PARTIAL", "Partial"

    id = AutoField(primary_key=True)
    characterid = ForeignKey(Character, related_name='characterversions', on_delete=PROTECT)
    versionkind = CharField(max_length=10, choices=CharacterVersionKind.choices, default=CharacterVersionKind.MAIN)
    picture = ForeignKey(Picture, related_name='characterversions', on_delete=PROTECT)
    isalive = BooleanField(default=True)
    isalterego = BooleanField(default=False)

    firstnameid = ForeignKey(FirstName, on_delete=PROTECT)
    familynameid = ForeignKey(FamilyName, on_delete=PROTECT)
    nickname = CharField(max_length=50, null=True)
    originname = CharField(max_length=50, null=True)
    fullname = CharField(max_length=100, db_column="fullname", editable=False)

    description = TextField(max_length=10000, null=True)
    strength = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    dexterity = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    endurance = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    power = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])
    experience = IntegerField(null=True, validators=[MinValueValidator(1), MaxValueValidator(20)])

    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = '"cha"."characterversion"'
        ordering = ["fullname"]  # TODO ordering by User status, first no superuser, no staff = Players

    def __str__(self):
        return self.fullname



class CharacterVersionToTagLink(Model):
    id = AutoField(primary_key=True)
    character = ForeignKey(Character, on_delete=CASCADE)
    tag = ForeignKey(Tag, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."characterversiontotaglink"'

