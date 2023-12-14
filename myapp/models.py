from django.db import models


class LicenseData(models.Model):
    windows_product_key = models.CharField(max_length=50,unique=True)
    license_expiration_date = models.DateTimeField(null=True)
    mac_address = models.CharField(max_length=17,unique=True)  # Assuming MAC addresses are stored as strings
    ip_address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    windows_version = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.windows_product_key} - {self.hostname}"
    
class WindowsInformation(models.Model):
    product_key = models.CharField(max_length=255)
    expiration_date = models.DateTimeField()
    mac_address = models.CharField(max_length=17)
    ip_address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    windows_version = models.CharField(max_length=255)
        
class SystemUsage(models.Model):
    product_key = models.CharField(max_length=255, unique=True)
    cpu_usage = models.FloatField()
    ram_usage = models.FloatField()
    disk_usage = models.CharField(max_length=255)
    unused_ram = models.FloatField()
    diskempty = models.FloatField()
    disk_info = models.FloatField()
    
# models.py
from django.db import models
from django.utils import timezone

class SystemStatus(models.Model):
    timestamp = models.DateTimeField(auto_now=True)  # Update timestamp on every save
    cpu_usage = models.FloatField()
    ram_usage = models.FloatField()
    disk_usage = models.FloatField()
    mac_address = models.CharField(max_length=17, unique=True)
    ip_address = models.GenericIPAddressField()
    hostname = models.CharField(max_length=255)
    network_usage = models.FloatField()
    defender_status = models.BooleanField()
    firewall_status = models.BooleanField()
    auto_updates_status = models.BooleanField()

    def save(self, *args, **kwargs):
        # Update the timestamp before saving
        self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.timestamp} - {self.hostname}"
    
    
## firewall models
from django.db import models

# models.py
class Firewall(models.Model):
    name = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    location = models.CharField(max_length=100)
    description = models.TextField()
    link = models.URLField()
