# Generated by Django 4.2 on 2023-06-02 15:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_variation_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='stock',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
