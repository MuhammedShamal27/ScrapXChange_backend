# Generated by Django 5.0.7 on 2024-10-16 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='latitude',
            field=models.DecimalField(decimal_places=7, max_digits=10),
        ),
        migrations.AlterField(
            model_name='shop',
            name='longitude',
            field=models.DecimalField(decimal_places=7, max_digits=10),
        ),
    ]