from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Model, CharField, ImageField, TextChoices, ForeignKey as FK,
    PROTECT, Manager, CASCADE, PositiveIntegerField, Index, IntegerField,
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


class PicturePositionManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('picture')
        return qs


class PicturePosition(Model):
    objects = PicturePositionManager()

    # technical fields of Generic relations
    content_type = FK(ContentType, related_name='pictures', on_delete=CASCADE)
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    picture = FK(Picture, related_name='picturepositions', on_delete=PROTECT)
    position = IntegerField(default=1)

    class Meta:
        indexes = [
            Index(fields=["content_type", "object_id"]),
        ]
        ordering = ['content_type', 'position', 'picture']

    def __str__(self):
        return f"{self.picture} (w: {self.content_object})"

