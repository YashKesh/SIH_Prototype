# Generated by Django 4.0.3 on 2023-12-20 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_temperaturereading'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temperaturereading',
            name='temperature',
            field=models.CharField(max_length=17),
        ),
    ]
