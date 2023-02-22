# Generated by Django 4.1.6 on 2023-02-22 17:31

from django.db import migrations, models
import resources.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(choices=[('CHARACTERS', 'characters'), ('LOCATIONS', 'locations'), ('ITEMS', 'items'), ('CREATURES', 'creatures'), ('SYMBOLS', 'symbols'), ('VARIA', 'varia')], max_length=20)),
                ('image', models.ImageField(blank=True, upload_to=resources.models.image_upload_path)),
            ],
            options={
                'db_table': '"res"."picture"',
                'ordering': ['title'],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('color', models.CharField(default='#000000', max_length=50)),
            ],
            options={
                'db_table': '"res"."tag"',
                'ordering': ['title'],
                'managed': False,
            },
        ),
    ]