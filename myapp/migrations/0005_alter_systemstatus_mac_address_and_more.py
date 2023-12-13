# Generated by Django 4.0.3 on 2023-12-13 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_systemstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemstatus',
            name='mac_address',
            field=models.CharField(max_length=17, unique=True),
        ),
        migrations.AlterField(
            model_name='systemstatus',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
