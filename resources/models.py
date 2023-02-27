from django.db.models import (
    Model, AutoField, CharField, ImageField, TextChoices, ForeignKey as FK,
    PROTECT,
)
from resources.utils import image_upload_path


#  ------------------------------------------------------------


class Picture(Model):

    class Category(TextChoices):
        CHARACTERS = "characters", "characters"
        CREATURES = "creatures", "creatures"
        ITEMS = "items", "items"
        LOCATIONS = "locations", "locations"
        SYMBOLS = "symbols", "symbols"
        USERS = "users", "users"
        VARIA = "varia", "varia"

    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True)
    category = CharField(max_length=20, choices=Category.choices)
    image = ImageField(upload_to=image_upload_path, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class PictureVersion(Model):
    picture = FK(Picture, related_name='pictureversions', on_delete=PROTECT)
    caption = CharField(max_length=100)

#  ------------------------------------------------------------
