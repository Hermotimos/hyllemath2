# Generated by Django 4.1.6 on 2023-02-24 19:19

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(blank=True, max_length=100, null=True)),
                ('_createdat', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='FamilyNameGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(max_length=10000)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FirstNameGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(max_length=10000)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FirstNameTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('color', models.CharField(default='#000000', max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='firstnametags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FirstName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('UNISEX', 'Unisex'), ('NONE', 'None')], default='MALE', max_length=6)),
                ('nominative', models.CharField(max_length=50, unique=True)),
                ('genitive', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(max_length=10000)),
                ('firstnamegroup', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='firstnames', to='characters.firstnamegroup')),
                ('origin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='originatedfirstnames', to='characters.firstname')),
                ('tags', models.ManyToManyField(blank=True, to='characters.firstnametag')),
            ],
            options={
                'ordering': ['nominative'],
            },
        ),
        migrations.CreateModel(
            name='FamilyNameTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('color', models.CharField(default='#000000', max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='familynametags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='FamilyName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nominative', models.CharField(max_length=50, unique=True)),
                ('nominative_pl', models.CharField(blank=True, max_length=50)),
                ('genitive', models.CharField(blank=True, max_length=50, null=True)),
                ('genitive_pl', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(max_length=10000)),
                ('familynamegroup', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='familynames', to='characters.familynamegroup')),
                ('origin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originatedfamilynames', to='characters.familyname')),
                ('tags', models.ManyToManyField(blank=True, related_name='familynames', to='characters.familynametag')),
            ],
            options={
                'ordering': ['nominative'],
            },
        ),
        migrations.CreateModel(
            name='CharacterVersionTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('color', models.CharField(default='#000000', max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='characterversiontags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='CharacterVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('versionkind', models.CharField(choices=[('DEAD', 'Dead'), ('MAIN', 'Main'), ('PAST', 'Past'), ('PARTIAL', 'Partial')], default='MAIN', max_length=10)),
                ('isalive', models.BooleanField(default=True)),
                ('isalterego', models.BooleanField(default=False)),
                ('nickname', models.CharField(blank=True, max_length=50, null=True)),
                ('originname', models.CharField(blank=True, max_length=50, null=True)),
                ('fullname', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=10000, null=True)),
                ('strength', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('dexterity', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('endurance', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('power', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('experience', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('_createdat', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='characterversions', to='characters.character')),
                ('familyname', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='characters.familyname')),
                ('firstname', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='characters.firstname')),
                ('picture', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='characterversions', to='resources.picture')),
                ('tags', models.ManyToManyField(blank=True, related_name='characterversions', to='characters.characterversiontag')),
            ],
            options={
                'ordering': ['fullname'],
            },
        ),
        migrations.AddIndex(
            model_name='firstnametag',
            index=models.Index(fields=['user'], name='characters__user_id_c399c3_idx'),
        ),
        migrations.AddIndex(
            model_name='firstname',
            index=models.Index(fields=['firstnamegroup'], name='characters__firstna_186915_idx'),
        ),
        migrations.AddIndex(
            model_name='firstname',
            index=models.Index(fields=['origin'], name='characters__origin__e5f98a_idx'),
        ),
        migrations.AddIndex(
            model_name='familynametag',
            index=models.Index(fields=['user'], name='characters__user_id_7f7d13_idx'),
        ),
        migrations.AddIndex(
            model_name='familyname',
            index=models.Index(fields=['familynamegroup'], name='characters__familyn_9f0875_idx'),
        ),
        migrations.AddIndex(
            model_name='familyname',
            index=models.Index(fields=['origin'], name='characters__origin__3a4f95_idx'),
        ),
        migrations.AddIndex(
            model_name='characterversiontag',
            index=models.Index(fields=['user'], name='characters__user_id_268335_idx'),
        ),
    ]