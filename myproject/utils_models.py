
from django.db.models import Model, CharField


class Tag(Model):
    title = CharField(max_length=50)
    color = CharField(max_length=50, default="#000000")

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title
