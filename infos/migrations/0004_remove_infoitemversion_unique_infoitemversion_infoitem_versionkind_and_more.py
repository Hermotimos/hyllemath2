# Generated by Django 4.1.7 on 2023-06-12 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infos', '0003_alter_infoitemposition_options_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='infoitemversion',
            name='unique_infoitemversion_infoitem_versionkind',
        ),
        migrations.AddConstraint(
            model_name='infoitemversion',
            constraint=models.UniqueConstraint(fields=('infoitem', 'versionkind'), name='unique_infoitemversion_infoitem_versionkind'),
        ),
    ]
