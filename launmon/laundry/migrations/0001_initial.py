# Generated by Django 5.0.5 on 2024-10-07 21:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('tzoffset', models.IntegerField(blank=True, null=True)),
                ('lastseen', models.DateTimeField(blank=True, null=True)),
                ('display_order', models.IntegerField(blank=True, null=True)),
                ('record_enable', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['site', 'section', 'display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('type', models.TextField(choices=[('W', 'washer'), ('D', 'dryer'), ('S', 'stack')], default='dryer')),
                ('processor', models.TextField(choices=[('generic', 'Generic'), ('generic_dryer', 'Generic Dryer'), ('generic_washer', 'Generic Washer'), ('speedqueen_washer', 'Speedqueen Washer'), ('whirlpool_washer', 'Whirlpool Washer'), ('maytag_stack', 'Maytag Stack')], default='generic')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('display_order', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['site', 'display_order', 'name'],
            },
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
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.TextField(blank=True, choices=[('wash', 'washing'), ('dry', 'drying'), ('both', 'both'), ('none', 'idle'), ('offline', 'offline'), ('ooo', 'out of order')], null=True)),
                ('time', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
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
        migrations.AddField(
            model_name='location',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.section'),
        ),
        migrations.AddField(
            model_name='section',
            name='site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='laundry.site'),
        ),
        migrations.AddField(
            model_name='location',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.site'),
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('code', models.TextField(blank=True, null=True)),
                ('ooo', models.BooleanField(blank=True, null=True)),
                ('time', models.DateTimeField(blank=True, null=True, unique=True)),
                ('fix_description', models.TextField(blank=True, null=True)),
                ('fix_time', models.DateTimeField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.site')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('device', models.CharField(blank=True, max_length=16, primary_key=True, serialize=False)),
                ('port', models.CharField(blank=True, max_length=6, null=True)),
                ('calibration', models.FloatField(blank=True, null=True)),
                ('cal_pow', models.FloatField(blank=True, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('location', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='laundry.site')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.TextField(blank=True, null=True)),
                ('subscription', models.TextField(blank=True, null=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
        ),
        migrations.CreateModel(
            name='UserSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.site')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rawcurrent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current', models.FloatField(null=True)),
                ('time', models.DateTimeField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='laundry.location')),
            ],
            options={
                'indexes': [models.Index(fields=['time'], name='time_idx')],
            },
        ),
    ]
