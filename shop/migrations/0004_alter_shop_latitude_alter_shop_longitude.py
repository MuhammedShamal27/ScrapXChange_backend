# Generated by Django 5.0.7 on 2024-10-04 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_shop_latitude_shop_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=100, null=True),
        ),
        migrations.AlterField(
            model_name='shop',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=100, null=True),
        ),
    ]
