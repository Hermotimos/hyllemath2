# Generated by Django 4.1.7 on 2023-06-12 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_alter_pictureposition_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='picture',
            name='category',
            field=models.CharField(choices=[('character', 'character'), ('creature', 'creature'), ('info', 'info'), ('item', 'item'), ('location', 'location'), ('locationtype', 'locationtype'), ('symbol', 'symbol'), ('user', 'user'), ('varia', 'varia')], max_length=20),
        ),
    ]
