# Generated by Django 4.2 on 2023-06-01 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_variation'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
