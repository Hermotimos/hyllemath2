# Generated by Django 4.1.6 on 2023-03-19 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import myproject.utils_models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('characters', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='characterversiontag',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characterversiontags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='characterversion',
            name='_createdby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='characterversionscreated', to='characters.character'),
        ),
        migrations.AddField(
            model_name='characterversion',
            name='character',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characterversions', to='characters.character'),
        ),
        migrations.AddField(
            model_name='characterversion',
            name='familyname',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characterversions', to='characters.familyname'),
        ),
        migrations.AddField(
            model_name='characterversion',
            name='firstname',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characterversions', to='characters.firstname'),
        ),
        migrations.AddField(
            model_name='characterversion',
            name='picture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='characterversions', to='resources.picture'),
        ),
        migrations.AddField(
            model_name='characterversion',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='characterversions', to='characters.characterversiontag'),
        ),
        migrations.AddField(
            model_name='character',
            name='user',
            field=models.ForeignKey(default=myproject.utils_models.get_gamemaster, on_delete=django.db.models.deletion.CASCADE, related_name='characters', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='knowledge',
            index=models.Index(fields=['content_type', 'object_id'], name='characters__content_63496c_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='firstnamegroup',
            unique_together={('title', 'parentgroup')},
        ),
        migrations.AlterUniqueTogether(
            name='characterversiontag',
            unique_together={('title', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='characterversion',
            unique_together={('character', 'picture', 'versionkind', 'fullname')},
        ),
    ]
