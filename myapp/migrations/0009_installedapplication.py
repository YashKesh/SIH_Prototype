# Generated by Django 4.0.3 on 2023-12-18 12:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_firewall'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstalledApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=50)),
                ('install_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('system_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.systemstatus')),
            ],
        ),
    ]
