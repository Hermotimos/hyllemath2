
from django.db.models import Model, CharField
from users.models import User


class Tag(Model):
    title = CharField(max_length=50)
    color = CharField(max_length=50, default="#000000")

    class Meta:
        abstract = True
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


def get_gamemaster() -> str:
    return User.objects.filter(is_superuser=True).first().id

