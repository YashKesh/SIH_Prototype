# Generated by Django 4.0.3 on 2023-12-12 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='licensedata',
            name='mac_address',
            field=models.CharField(max_length=17, unique=True),
        ),
        migrations.AlterField(
            model_name='licensedata',
            name='windows_product_key',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
