
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CharField, Model

from users.models import User


class Tag(Model):
    title = CharField(max_length=50)
    color = CharField(max_length=50, default="#000000")

    class Meta:
        abstract = True
        ordering = ['title']

    def __str__(self):
        return self.title


def get_gamemaster() -> str:
    default_gamemaster = User.objects.filter(is_superuser=True).last().id
    return default_gamemaster


def min_max(min: int, max: int) -> list:
    return [MinValueValidator(min), MaxValueValidator(max)]
