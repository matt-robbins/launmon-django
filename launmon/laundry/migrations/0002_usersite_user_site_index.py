# Generated by Django 5.0.5 on 2024-10-09 22:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laundry', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='usersite',
            index=models.Index(fields=['user', 'site'], name='user_site_index'),
        ),
    ]
