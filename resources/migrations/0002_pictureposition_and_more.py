# Generated by Django 4.1.7 on 2023-06-10 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PicturePosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('position', models.IntegerField(default=1)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='contenttypes.contenttype')),
                ('picture', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='picturepositions', to='resources.picture')),
            ],
            options={
                'ordering': ['content_type', 'picture', 'position'],
            },
        ),
        migrations.RemoveField(
            model_name='pictureversionposition',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='pictureversionposition',
            name='pictureversion',
        ),
        migrations.DeleteModel(
            name='PictureVersion',
        ),
        migrations.DeleteModel(
            name='PictureVersionPosition',
        ),
        migrations.AddIndex(
            model_name='pictureposition',
            index=models.Index(fields=['content_type', 'object_id'], name='resources_p_content_20dd0d_idx'),
        ),
    ]