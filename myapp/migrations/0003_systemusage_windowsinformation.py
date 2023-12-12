# Generated by Django 4.0.3 on 2023-12-12 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_licensedata_mac_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_key', models.CharField(max_length=255, unique=True)),
                ('cpu_usage', models.FloatField()),
                ('ram_usage', models.FloatField()),
                ('disk_usage', models.CharField(max_length=255)),
                ('unused_ram', models.FloatField()),
                ('diskempty', models.FloatField()),
                ('disk_info', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='WindowsInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_key', models.CharField(max_length=255)),
                ('expiration_date', models.DateTimeField()),
                ('mac_address', models.CharField(max_length=17)),
                ('ip_address', models.GenericIPAddressField()),
                ('hostname', models.CharField(max_length=255)),
                ('windows_version', models.CharField(max_length=255)),
            ],
        ),
    ]