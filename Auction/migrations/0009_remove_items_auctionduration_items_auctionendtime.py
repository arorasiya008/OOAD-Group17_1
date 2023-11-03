# Generated by Django 4.2.6 on 2023-11-03 19:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Auction', '0008_items_timebuffer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='items',
            name='auctionDuration',
        ),
        migrations.AddField(
            model_name='items',
            name='auctionEndTime',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
