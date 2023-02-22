from django.db.models import (
    CASCADE, Model, AutoField, CharField, ForeignKey, Index, ImageField,
    TextChoices,
)
from resources.utils import image_upload_path



class Tag(Model):
    id = AutoField(primary_key=True)
    author = ForeignKey("users.User", related_name='tags', null=True, blank=True, on_delete=CASCADE)
    title = CharField(max_length=50)
    color = CharField(max_length=50, default="#000000")

    class Meta:
        managed = False
        db_table = '"res"."tag"'
        indexes = [
            Index(fields=["author"])
        ]
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title






# # Pierwotna wersja tej funkcji, zobaczyć czy nie będzie potrzebna w kontekście GCP
# def image_upload_path(instance, filename):
#     from django.conf import settings
#     print(settings.MEDIA_ROOT + '/{0}/{1}'.format(instance.category, filename))
#     return settings.MEDIA_ROOT + '/{0}/{1}'.format(instance.category, filename)


class Picture(Model):

    class Category(TextChoices):
        CHARACTERS = "characters", "characters"
        LOCATIONS = "locations", "locations"
        ITEMS = "items", "items"
        CREATURES = "creatures", "creatures"
        SYMBOLS = "symbols", "symbols"
        VARIA = "varia", "varia"

    id = AutoField(primary_key=True)
    title = CharField(max_length=100, unique=True)
    category = CharField(max_length=20, choices=Category.choices)
    image = ImageField(upload_to=image_upload_path, blank=True)

    class Meta:
        db_table = '"res"."picture"'
        managed = False
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

