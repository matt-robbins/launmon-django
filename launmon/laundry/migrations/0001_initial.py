# Generated by Django 5.0.5 on 2024-05-08 19:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.TextField(blank=True, null=True)),
                ('tzoffset', models.IntegerField(blank=True, null=True)),
                ('lastseen', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('address', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('time', models.DateTimeField(blank=True, null=True, unique=True)),
                ('fix_description', models.TextField(blank=True, null=True)),
                ('fix_time', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(db_column='location', on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.TextField(blank=True, choices=[('wash', 'washing'), ('dry', 'drying'), ('both', 'both'), ('none', 'idle')], null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('device', models.CharField(blank=True, max_length=16, primary_key=True, serialize=False)),
                ('port', models.CharField(blank=True, max_length=6, null=True)),
                ('calibration', models.FloatField(blank=True, null=True)),
                ('cal_pow', models.FloatField(blank=True, null=True)),
                ('changed', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='laundry.location')),
            ],
        ),
        migrations.CreateModel(
            name='Calibration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calibration', models.FloatField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.locationtype'),
        ),
        migrations.CreateModel(
            name='Rawcurrent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current', models.FloatField(blank=True, null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
        ),
        migrations.AddField(
            model_name='location',
            name='site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.site'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.TextField(blank=True, null=True)),
                ('subscription', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(db_column='location', on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
        ),
    ]
