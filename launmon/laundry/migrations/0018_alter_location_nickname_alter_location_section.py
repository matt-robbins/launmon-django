# Generated by Django 5.0.5 on 2024-06-03 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laundry', '0017_alter_location_options_location_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='nickname',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='section',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
