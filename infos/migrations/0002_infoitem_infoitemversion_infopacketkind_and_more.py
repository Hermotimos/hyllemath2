# Generated by Django 4.1.7 on 2023-06-04 10:59

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.comparison


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0006_remove_characterversion_unique_character_for_mainversion_and_more'),
        ('infos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enigmalevel', models.CharField(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3')], default='0', max_length=1)),
                ('_mainversiontitle', models.CharField(blank=True, max_length=150, null=True)),
                ('_createdat', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='infoitemsauthored', to='characters.character')),
            ],
            options={
                'ordering': ['enigmalevel', '_mainversiontitle'],
            },
        ),
        migrations.CreateModel(
            name='InfoItemVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('versionkind', models.CharField(choices=[('1. MAIN', 'MAIN'), ('2. PARTIAL', 'PARTIAL'), ('3. PAST', 'PAST'), ('4. BYPLAYER', 'BYPLAYER')], default='1. MAIN', max_length=15)),
                ('title', models.CharField(max_length=100)),
                ('text', models.TextField()),
                ('_createdat', models.DateTimeField(auto_now_add=True)),
                ('_comment', models.TextField(blank=True, max_length=1000, null=True)),
                ('_createdby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='infoitemversionscreated', to='characters.character')),
                ('infoitem', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='infoitemversions', to='infos.infoitem')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='InfoPacketKind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('locationordering', models.IntegerField(blank=True, null=True)),
                ('characterordering', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['locationordering', 'characterordering', 'name'],
            },
        ),
        migrations.AlterModelOptions(
            name='infopacket',
            options={'ordering': [django.db.models.functions.comparison.Collate('title', 'pl-PL-x-icu')]},
        ),
        migrations.RemoveField(
            model_name='infopacket',
            name='author',
        ),
        migrations.RemoveField(
            model_name='infopacket',
            name='infopacketkind',
        ),
        migrations.RemoveField(
            model_name='infopacket',
            name='informees',
        ),
        migrations.RemoveField(
            model_name='infopacket',
            name='ininfopackets',
        ),
        migrations.RemoveField(
            model_name='infopacket',
            name='text',
        ),
        migrations.DeleteModel(
            name='InfoPacketPosition',
        ),
        migrations.AddField(
            model_name='infopacket',
            name='infoitems',
            field=models.ManyToManyField(blank=True, related_name='infopackets', to='infos.infoitem'),
        ),
        migrations.AddField(
            model_name='infopacket',
            name='infopacketkinds',
            field=models.ManyToManyField(blank=True, related_name='infopackets', to='infos.infopacketkind'),
        ),
    ]
