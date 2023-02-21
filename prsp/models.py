from django.db.models import (
    CASCADE, PROTECT, SET_NULL, EnumField, TextChoices, Model,
    AutoField, CharField, ForeignKey, Index,
    IntegerField, TextField
)



"""

chatGPT

1. use direct imports of field types and other features and never use "models." syntax; use these:
from django.db.models import (
    CASCADE, PROTECT, SET_NULL, EnumField, TextChoices, Model,
    AutoField, CharField, ForeignKey, Index,
    IntegerField, TextField
)

2. for Gender enum use EnumField and declare its class withing FirstName class

3. declare models as unmanaged

4. create __str__ methods with self.title whenever possible, elsewhere guess and add comment "check it!"

5. create get_absolute_url methods with the following schema, replacing MODELNAME with lowercase name of the model
    return reverse('prsp:MODELNAME', kwargs={'MODELNAME_id' : self.id})

paste

"""