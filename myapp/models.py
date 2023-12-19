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
    
## installed applications 
# models.py

# models.py
from django.db import models

class InstalledApp(models.Model):
    name = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255,null = True)
    version = models.CharField(max_length=50)
    mac_address = models.CharField(max_length=17)  # Assuming MAC address is stored as a string

    def __str__(self):
        return self.name

## end of the installed
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



### linux distribution system 
# monitor_app/models.py
from django.db import models

class MonitoringData(models.Model):
    timestamp = models.DateTimeField()
    mac_id = models.CharField(max_length=17,unique=True)
    ip_address = models.CharField(max_length=15)
    linux_distribution = models.CharField(max_length=255)
    cpu_usage = models.FloatField()
    ram_usage = models.FloatField()
    disk_usage = models.FloatField()
    sent_mb = models.FloatField()
    received_mb = models.FloatField()
    host_name = models.CharField(max_length=255)
    # Add fields for device location if available

    def __str__(self):
        return f"MonitoringData - {self.timestamp}"
    
####
### router db 
# models.py
from django.db import models

class Router(models.Model):
    Name = models.CharField(max_length=255,default = None)
    IP_address = models.GenericIPAddressField()
    router_type = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default = 0000)
    category = models.CharField(max_length=255)
    vendor = models.CharField(max_length=255)
    poll_using = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.vendor} Router ({self.IP_address})"
    
    
### end of router db ###
