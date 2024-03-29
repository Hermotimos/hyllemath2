# Generated by Django 4.1.7 on 2023-06-10 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('resources', '0001_initial'),
        ('locations', '0001_initial'),
        ('characters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationversion',
            name='picture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locationversions', to='resources.picture'),
        ),
        migrations.AddField(
            model_name='locationversion',
            name='propername',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locationversions', to='locations.locationname'),
        ),
        migrations.AddField(
            model_name='locationtype',
            name='defaultpicture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locationtypes', to='resources.picture'),
        ),
        migrations.AddField(
            model_name='locationname',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='locationnames', to='locations.locationnametag'),
        ),
        migrations.AddField(
            model_name='location',
            name='_createdby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='createdlocations', to='characters.character'),
        ),
        migrations.AddField(
            model_name='location',
            name='inlocation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='locations.location'),
        ),
        migrations.AddField(
            model_name='location',
            name='locationtype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='locations.locationtype'),
        ),
        migrations.AddConstraint(
            model_name='locationversion',
            constraint=models.UniqueConstraint(fields=('location', 'versionkind', 'picture', 'propername', 'descriptivename'), name='unique_locationversion_location_versionkind_picture_propername_descriptivename'),
        ),
        migrations.AddConstraint(
            model_name='locationversion',
            constraint=models.UniqueConstraint(condition=models.Q(('versionkind', '1. MAIN')), fields=('location',), name='unique_locationversion_main'),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together={('locationtype', '_mainversionname')},
        ),
    ]
