# Generated by Django 4.1.6 on 2023-03-19 17:26

from django.db import migrations, models
import django.db.models.deletion
import resources.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(choices=[('character', 'character'), ('creature', 'creature'), ('item', 'item'), ('location', 'location'), ('locationtype', 'locationtype'), ('symbol', 'symbol'), ('user', 'user'), ('varia', 'varia')], max_length=20)),
                ('image', models.ImageField(blank=True, upload_to=resources.utils.image_upload_path)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='PictureVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('picture', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pictureversions', to='resources.picture')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
