from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, SET_DEFAULT, TextChoices, Model, Manager, F,
    CharField, ForeignKey as FK, DateTimeField, PositiveIntegerField,
    IntegerField, PositiveSmallIntegerField, TextField, BooleanField,
    ManyToManyField as M2M,
)
from django.db.models.functions import Collate
from django.utils.html import format_html

from characters.models import Knowledge
from myproject.utils_models import Tag
from resources.models import Picture


#  ------------------------------------------------------------


class LocationNameTag(Tag):
    # add unique constraint as this is for GM use only
    title = CharField(max_length=50, unique=True)
    ordernum = IntegerField()

    # TODO stworzyć:
    # KAZDY,
    # OBSZAR,
    # OSIEDLE, RZEKA, WYSPA,
    # JEZIORO, DOLINA, GÓRY,
    # MORZA, ... ?

    class Meta:
        ordering = ["ordernum"]

    def __str__(self):
        return self.title


#  ------------------------------------------------------------


class LocationNameManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('locationnametags')
        return qs


class LocationName(Model):
    objects = LocationNameManager()

    nominative = CharField(max_length=100, unique=True)
    genitive = CharField(max_length=100, blank=True, null=True)
    equivalents = ArrayField(CharField(max_length=100), blank=True)
    locationnametags = M2M(LocationNameTag, related_name="locationnames")
    meaning = TextField(max_length=1000, blank=True, null=True)
    description = TextField(max_length=1000, blank=True, null=True)

    class Meta:
        ordering = [Collate('nominative', 'pl-PL-x-icu')]

    def __str__(self):
        return self.nominative

    # TODO in save method ensure if "river" is chosen as LocationNameKind
    # and specific region with property of "river=village=name" is assigned,
    # then "vilage" and "name" are also added to M2M


#  ------------------------------------------------------------


class LocationType(Model):
    name = CharField(unique=True, max_length=100)
    namepl = CharField(max_length=100, blank=True, null=True)
    defaultpicture = FK(
        Picture, related_name='locationtypes', on_delete=PROTECT,
        blank=True, null=True,)
    hierarchynum = PositiveSmallIntegerField()

    class Meta:
        ordering = ['hierarchynum']

    def __str__(self):
        return self.name


#  ------------------------------------------------------------


class LocationManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('inlocation')
        return qs


class Location(Model):
    objects = LocationManager()

    name = FK(LocationName, related_name='locations', on_delete=PROTECT)
    locationtype = FK(LocationType, related_name='locations', on_delete=PROTECT)
    inlocation = FK(
        to='self', related_name='locations', on_delete=PROTECT,
        blank=True, null=True)

    class Meta:
        unique_together = ['name', 'locationtype']

    def __str__(self):
        return self.name


#  ------------------------------------------------------------


class LocationVersionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'location', 'mainpicture',
            # 'mainaudio',
        )
        return qs


class LocationVersion(Model):
    objects = LocationVersionManager()

    location = FK(Location, related_name='locationversions', on_delete=PROTECT)
    # TODO: czy tu paketyzacja?
    description = TextField(blank=True, null=True)
    comment = TextField(max_length=1000, blank=True, null=True)
    mainpicture = FK(
        to=Picture, related_name='locationversions', on_delete=PROTECT,
        blank=True, null=True)
    _createdat = DateTimeField(auto_now_add=True)
    # TODO players see DISTINCT ON (location) ORDER BY _createdat DESC

    # mainaudio = FK(
    #     to=Audio, related_name='locationversions', on_delete=PROTECT,
    #     blank=True, null=True)
    # picturesets = M2M(to=PictureSet, related_name='locationversions', blank=True)
    # audiosets = M2M(AudioSet, related_name='locationversions', blank=True)
    # infopackets = M2M(to=InfoPacket, related_name='locationversions', blank=True)

    knowledges = GenericRelation(Knowledge)

    class Meta:
        ordering = ['location', '-_createdat']

    def __str__(self):
        return self.location.name.nominative

    # TODO
    # def get_absolute_url(self):
    #     return settings.BASE_URL + reverse('toponomikon:location', kwargs={'location_id' : self.id})

    # def informables(self, current_profile):
    #     qs = current_profile.character.acquaintanceships()
    #     qs = qs.exclude(
    #         known_character__profile__in=(self.participants.all() | self.informees.all())
    #     ).filter(
    #         known_character__profile__in=Profile.active_players.all())
    #     return qs

    def with_sublocations(self):
        with_sublocs = Location.objects.raw(f"""
            WITH RECURSIVE sublocations AS (
                SELECT * FROM locations_location WHERE id = {self.pk}
                UNION ALL
                SELECT loc.*
                FROM locations_location AS loc
                JOIN sublocations AS subloc ON loc.in_location_id = subloc.id
            )
            SELECT * FROM sublocations;
        """)
        return with_sublocs




# class PrimaryLocationManager(Manager):
#     def get_queryset(self):
#         qs = super().get_queryset()
#         qs = qs.filter(in_location=None)
#         return qs


# class PrimaryLocation(Location):
#     objects = PrimaryLocationManager()

#     class Meta:
#         proxy = True
#         verbose_name = '--- Primary Location'
#         verbose_name_plural = '--- Primary Locations'


# class SecondaryLocationManager(Manager):
#     def get_queryset(self):
#         qs = super().get_queryset()
#         qs = qs.exclude(in_location=None)
#         return qs


# class SecondaryLocation(Location):
#     objects = SecondaryLocationManager()

#     class Meta:
#         proxy = True
#         verbose_name = '--- Secondary Location'
#         verbose_name_plural = '--- Secondary Locations'
