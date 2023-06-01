# Generated by Django 4.2 on 2023-05-26 14:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=250)),
                ('address_line_1', models.CharField(max_length=50)),
                ('address_line_2', models.CharField(blank=True, max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=10, null=True)),
                ('status', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
