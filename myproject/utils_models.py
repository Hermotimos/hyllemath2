
from django.db.models import Model, CharField, F


class Tag(Model):
    title = CharField(max_length=50)
    color = CharField(max_length=50, default="#000000")

    class Meta:
        abstract = True
        # user FK field is added in subclasses
        ordering = [
            F('user').asc(nulls_first=True),
            'title',
        ]

    def __str__(self) -> str:
        return self.title
