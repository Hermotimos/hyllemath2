# Generated by Django 4.1.7 on 2023-06-10 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='infoitemversion',
            name='versioncomment',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='infoitem',
            name='enigmalevel',
            field=models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], default='0', max_length=1),
        ),
    ]
