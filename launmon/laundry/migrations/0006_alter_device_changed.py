# Generated by Django 5.0.5 on 2024-05-12 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laundry', '0005_alter_device_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='changed',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
