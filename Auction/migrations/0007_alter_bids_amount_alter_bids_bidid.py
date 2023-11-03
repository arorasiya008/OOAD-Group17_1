# Generated by Django 4.2.6 on 2023-11-03 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auction', '0006_alter_items_costprice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='bids',
            name='bidId',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]