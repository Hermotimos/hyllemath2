from django.db.models import (
    CASCADE, PROTECT, SET_NULL, TextChoices, Model,
    AutoField, CharField, ForeignKey as FK, Index, DateTimeField,
    IntegerField, TextField, BooleanField, ManyToManyField as M2M
)
from django.core.validators import MinValueValidator, MaxValueValidator

from resources.models import Picture
from myproject.utils_models import Tag


# TODO: check if Django uses indexes on "id" fields even if they aren't mentioned in Meta - speed tests
# TODO: add absolute_url when applicable


#  ------------------------------------------------------------


class FirstNameTag(Tag):
    author = FK(
        "users.User", related_name='firstnametags',
        null=True, blank=True, on_delete=CASCADE)

    class Meta:
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ['title']


class FirstNameGroup(Model):
    title = CharField(max_length=100, unique=True)
    description = TextField(max_length=10000)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title



class FirstName(Model):

    class Gender(TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        UNISEX = "UNISEX", "Unisex"
        NONE = "NONE", "None"

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
        indexes = [
            Index(fields=["firstnamegroup"]),
            Index(fields=["origin"]),
        ]
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


#  ------------------------------------------------------------


class FamilyNameTag(Tag):
    author = FK(
        "users.User", related_name='familynametags',
        null=True, blank=True, on_delete=CASCADE)

    class Meta:
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ['title']


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
        indexes = [
            Index(fields=["familynamegroup"]),
            Index(fields=["origin"]),
        ]
        ordering = ["nominative"]

    def __str__(self):
        return self.nominative


#  ------------------------------------------------------------


class Character(Model):
    user = FK("users.User", related_name='characters', on_delete=CASCADE)
    fullname = CharField(max_length=100, null=True, blank=True)
    _createdat = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["user"]

    def __str__(self):
        return self.fullname


    # def __str__(self):
    #     greatest_v = CharacterVersion.objects.filter(character__id=self.id).order_by("versionkind").first()
    #     return f"[{self.user.username}] - {greatest_v.fullname} ({greatest_v.versionkind})"



class CharacterVersionTag(Tag):
    author = FK(
        "users.User", related_name='characterversiontags',
        null=True, blank=True, on_delete=CASCADE)

    class Meta:
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ['title']


class CharacterVersion(Model):

    class CharacterVersionKind(TextChoices):
        DEAD = "DEAD", "Dead"
        MAIN = "MAIN", "Main"
        PAST = "PAST", "Past"
        PARTIAL = "PARTIAL", "Partial"

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

    _createdat = DateTimeField(auto_now_add=True)
    tags = M2M(CharacterVersionTag, related_name='characterversions', blank=True)

    class Meta:
        ordering = ["fullname"]

    def __str__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        firstname = getattr(self.firstname, 'nominative', "")
        familyname = getattr(self.familyname, 'nominative', "")
        nickname = self.nickname or ""
        originname = self.originname or ""

        self.fullname = f"{firstname} {familyname} {nickname} {originname}".replace('  ', ' ').strip()
        self.character.fullname = self.fullname
        self.character.save()

        super().save(*args, **kwargs)


#  ------------------------------------------------------------
