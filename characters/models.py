from django.db.models import (
    CASCADE, PROTECT, SET_NULL, TextChoices, Model,
    AutoField, CharField, ForeignKey as FK, Index, DateTimeField,
    IntegerField, TextField, BooleanField, ManyToManyField as M2M
)
from django.core.validators import MinValueValidator, MaxValueValidator

from resources.models import Picture
from myproject.utils_models import Tag

# TODO: check if Django uses indexes on "id" fields even if they aren"t mentioned in Meta - speed tests
# TODO: add ordering
# TODO: add absolute_url when applicable


#  ------------------------------------------------------------


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
    gender = CharField(max_length=6, choices=Gender.choices, default=Gender.MALE)
    firstnamegroup = FK(
        FirstNameGroup, db_column="firstnamegroupid",
        related_name='firstnames',
        on_delete=PROTECT)
    origin = FK(
        "self", db_column="originid",
        related_name='originatedfirstnames',
        null=True, blank=True, on_delete=PROTECT)
    nominative = CharField(max_length=50, unique=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000)
    tags = M2M("FirstNameTag", through="FirstNameM2MFirstNameTag", blank=True)

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


class FirstNameTag(Tag):
    author = FK(
        "users.User", db_column="authorid", related_name='firstnametags',
        null=True, blank=True, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"res"."firstnametag"'
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ['title']


class FirstNameM2MFirstNameTag(Model):
    id = AutoField(primary_key=True)
    firstname = FK(FirstName, db_column="firstnameid", on_delete=CASCADE)
    firstnametag = FK(FirstNameTag, db_column="firstnametagid", on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."firstnamem2mfirstnametag"'


# #  ------------------------------------------------------------


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
    familynamegroup = FK(
        FamilyNameGroup,
        db_column="familynamegroupid",
        related_name='familynames', on_delete=PROTECT)
    origin = FK(
        "self", db_column="originid",
        related_name='originatedfamilynames',
        null=True, blank=True,
        on_delete=SET_NULL)
    nominative = CharField(max_length=50, unique=True)
    nominative_pl = CharField(max_length=50, blank=True)
    genitive = CharField(max_length=50, blank=True, null=True)
    genitive_pl = CharField(max_length=50, blank=True, null=True)
    description = TextField(max_length=10000)
    tags = M2M(
        "FamilyNameTag", through="FamilyNameM2MFamilyNameTag",
        related_name='familynames',
        blank=True)

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




class FamilyNameTag(Tag):
    author = FK(
        "users.User", db_column="authorid", related_name='familynametags',
        null=True, blank=True, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."familynametag"'
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ['title']



class FamilyNameM2MFamilyNameTag(Model):
    id = AutoField(primary_key=True)
    familyname = FK(FamilyName, db_column="familynameid", on_delete=CASCADE)
    familynametag = FK(FamilyNameTag, db_column="familynametagid", on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."familynamem2mfamilynametag"'


# # #  ------------------------------------------------------------


class Character(Model):
    id = AutoField(primary_key=True)
    user = FK("users.User", related_name='characters', on_delete=CASCADE)
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
    characterid = FK(Character, related_name='characterversions', on_delete=PROTECT)
    versionkind = CharField(max_length=10, choices=CharacterVersionKind.choices, default=CharacterVersionKind.MAIN)
    picture = FK(Picture, related_name='characterversions', on_delete=PROTECT)
    isalive = BooleanField(default=True)
    isalterego = BooleanField(default=False)

    firstnameid = FK(FirstName, on_delete=PROTECT)
    familynameid = FK(FamilyName, on_delete=PROTECT)
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
    tags = M2M(
        "CharacterVersionTag", through="CharacterVersionM2MCharacterVersionTag",
        related_name='familynames', blank=True)

    class Meta:
        managed = False
        db_table = '"cha"."characterversion"'
        ordering = ["fullname"]  # TODO ordering by User status, first no superuser, no staff = Players

    def __str__(self):
        return self.fullname



class CharacterVersionTag(Tag):
    author = FK(
        "users.User", db_column="authorid", related_name='characterversiontags',
        null=True, blank=True, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."charactertag"'
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ['title']


class CharacterVersionM2MCharacterVersionTag(Model):
    id = AutoField(primary_key=True)
    characterversion = FK(CharacterVersion, on_delete=CASCADE)
    characterversiontag = FK(CharacterVersionTag, on_delete=CASCADE)

    class Meta:
        managed = False
        db_table = '"cha"."characterversionm2mcharacterversiontag"'


# # #  ------------------------------------------------------------
