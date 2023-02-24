
from django.db.models import Model, AutoField, CharField, Index


class Tag(Model):
    id = AutoField(primary_key=True)
    title = CharField(max_length=50)
    color = CharField(max_length=50, default="#000000")

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.title
