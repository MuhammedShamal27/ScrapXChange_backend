# Generated by Django 5.0.7 on 2024-10-04 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_remove_shop_latitude_remove_shop_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=50, max_digits=100, null=True),
        ),
        migrations.AddField(
            model_name='shop',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=50, max_digits=100, null=True),
        ),
    ]
