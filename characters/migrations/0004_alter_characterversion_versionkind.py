# Generated by Django 4.1.7 on 2023-03-05 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0003_alter_characterversion_dexterity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characterversion',
            name='versionkind',
            field=models.CharField(choices=[('1. DEAD', 'DEAD'), ('2. MAIN', 'MAIN'), ('3. CHANGED', 'CHANGED'), ('4. PARTIAL', 'PARTIAL'), ('5. PAST', 'PAST'), ('6. BYUSER', 'BYUSER')], default='2. MAIN', max_length=10),
        ),
    ]
