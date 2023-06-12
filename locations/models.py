from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, SET_DEFAULT, TextChoices, Model, Manager, F,
    CharField, ForeignKey as FK, DateTimeField, PositiveIntegerField,
    IntegerField, PositiveSmallIntegerField, TextField, BooleanField,
    ManyToManyField as M2M, UniqueConstraint, Q, OneToOneField,
)
from django.db.models.functions import Collate
from django.utils.html import format_html

from myproject.utils_models import Tag
from resources.models import Picture


#  ------------------------------------------------------------


class LocationNameTag(Tag):
    # unique constraint as this is for GM use only
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
        qs = qs.prefetch_related('tags')
        return qs


class LocationName(Model):
    objects = LocationNameManager()

    nominative = CharField(max_length=100)
    genitive = CharField(max_length=100, blank=True, null=True)
    adjectiveroot = CharField(max_length=100, blank=True, null=True)
    equivalents = ArrayField(CharField(max_length=100), blank=True, null=True)
    description = TextField(max_length=1000, blank=True, null=True)
    tags = M2M(LocationNameTag, related_name="locationnames", blank=True)

    class Meta:
        ordering = [Collate('nominative', 'pl-PL-x-icu')]

    def __str__(self):
        return self.nominative

    def save(self, *args, **kwargs):
        self.genitive = self.genitive.title()
        super().save(*args, **kwargs)
        # Call related objects' save() to reevaluate Location.name
        for location in self.locations.all():
            location.save()

    # TODO in save method ensure if "river" is chosen as LocationNameKind
    # and specific region with property of "river=village=name" is assigned,
    # then "vilage" and "name" are also added to M2M


#  ------------------------------------------------------------


class LocationTypeManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('defaultpicture')
        return qs


class LocationType(Model):
    objects = LocationTypeManager()

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
        qs = qs.select_related('inlocation', 'locationtype')
        return qs


class Location(Model):
    objects = LocationManager()

    locationtype = FK(LocationType, related_name='locations', on_delete=PROTECT)
    inlocation = FK(
        to='self', related_name='locations', on_delete=PROTECT,
        blank=True, null=True)
    _mainversionname = CharField(max_length=150, blank=True, null=True)
    _createdat = DateTimeField(auto_now_add=True)
    _createdby = FK(
        'characters.Character', related_name='createdlocations',
        on_delete=PROTECT, blank=True, null=True)

    class Meta:
        ordering = ['_mainversionname']
        unique_together = ['locationtype', '_mainversionname']

    def __str__(self):
        if self._mainversionname:
            return str(self._mainversionname)
        return f"{self.user.username} - {self.id}"


#  ------------------------------------------------------------


class LocationVersionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'location', 'propername', 'picture',
            # 'mainaudio',
        )
        return qs


class LocationVersion(Model):
    objects = LocationVersionManager()

    class LocationVersionKind(TextChoices):
        MAIN = "1. MAIN", "MAIN"
        PARTIAL = "2. PARTIAL", "PARTIAL"
        PAST = "3. PAST", "PAST"
        BYPLAYER = "4. BYPLAYER", "BYPLAYER"

    location = FK(Location, related_name='locationversions', on_delete=PROTECT)
    versionkind = CharField(
        max_length=15, choices=LocationVersionKind.choices,
        default=LocationVersionKind.MAIN)
    versioncomment = TextField(max_length=1000, blank=True, null=True)    # Field for the reason the version exists

    # versioned stuff
    picture = FK(
        to=Picture, related_name='locationversions', on_delete=PROTECT,
        blank=True, null=True)
    propername = FK(
        LocationName, related_name='locationversions', on_delete=PROTECT,
        blank=True, null=True)
    descriptivename = CharField(max_length=100, blank=True, null=True) # In case no propername
    name = CharField(max_length=100)    # redundantne, wygodniejsze od property
    description = TextField(blank=True, null=True)      # TODO: czy tu paketyzacja?
    population = PositiveIntegerField(blank=True, null=True)

    # mainaudio = FK(
    #     to=Audio, related_name='locationversions', on_delete=PROTECT,
    #     blank=True, null=True)
    # audiosets = M2M(AudioSet, related_name='locationversions', blank=True)
    infopacketset = OneToOneField(
        'infos.InfoPacketSet', on_delete=PROTECT, blank=True, null=True)
    knowledges = GenericRelation('characters.Knowledge')

    _createdat = DateTimeField(auto_now_add=True)   # TODO players see DISTINCT ON (location) ORDER BY _createdat DESC

    class Meta:
        ordering = ['location', '-_createdat']
        constraints = [
            UniqueConstraint(
                fields=['location', 'versionkind', 'picture', 'propername', 'descriptivename'],
                name='unique_locationversion_location_versionkind_picture_propername_descriptivename'),
            UniqueConstraint(
                fields=['location'],
                condition=Q(versionkind="1. MAIN"),
                name='unique_locationversion_main')
        ]

    def __str__(self):
        return f"{self.name} ({self.versionkind[3:]})"

    def save(self, *args, **kwargs):
        # reevaluate name on each save; called by LocationName.save()
        self.name = str(self.propername) or self.descriptivename

        # When updating MAIN version, update related model's _mainversionname
        if self.versionkind == '2. MAIN':
            self.character._mainversionname = self.fullname
            self.character.save()

        super().save(*args, **kwargs)

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


    # TODO przekształcić, może wyekspediować do funkcji wołającej to na podstawie request.user?
    #  Przyjrzeć się dokładnie co to robi w Hyllemath 1.0 i gdzie jest używane
    # Być może rozbić na dwie osobne funkcje, jedna do Location,
    # druga do zbierania z wyników pierwszej LocationVersion
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


# TODO Proxies - przyjrzeć się czy są potrzebne, zwłaszcza jak mam linki do edycji ze strony

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
