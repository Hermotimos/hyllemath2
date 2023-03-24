from django.db.models import (
    Model, CharField, ImageField, TextChoices, ForeignKey as FK,
    PROTECT, Manager,
)
from resources.utils import image_upload_path


#  ------------------------------------------------------------


class PictureManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('characterversions', 'locationversions')
        return qs


class Picture(Model):
    objects = PictureManager()

    class Category(TextChoices):
        CHARACTER = "character", "character"
        CREATURE = "creature", "creature"
        ITEM = "item", "item"
        LOCATION = "location", "location"
        LOCATIONTYPE = "locationtype", "locationtype"
        SYMBOL = "symbol", "symbol"
        USER = "user", "user"
        VARIA = "varia", "varia"

    title = CharField(max_length=100, unique=True)
    category = CharField(max_length=20, choices=Category.choices)
    image = ImageField(upload_to=image_upload_path, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


#  ------------------------------------------------------------


class PictureVersion(Model):
    picture = FK(Picture, related_name="pictureversions", on_delete=PROTECT)
    title = CharField(max_length=100, unique=True)

    # TODO this class is for GameEvent (or Event in general), maybe InfoPacket

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f"[{self.picture.title}]: {self.title}"

