# Generated by Django 4.1.7 on 2023-06-10 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0003_characterknowninfoitemversion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='characterknowncharacterversion',
            options={'verbose_name': 'Character - known Character Version'},
        ),
        migrations.AlterModelOptions(
            name='characterknowninfoitemversion',
            options={'verbose_name': 'Character - known Info Item Version'},
        ),
        migrations.AlterModelOptions(
            name='characterknownlocationversion',
            options={'verbose_name': 'Character - known Location Version'},
        ),
    ]