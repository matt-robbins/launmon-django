# Generated by Django 5.0.5 on 2024-06-03 16:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laundry', '0020_section_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.section'),
        ),
        migrations.AlterField(
            model_name='location',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.site'),
        ),
    ]
