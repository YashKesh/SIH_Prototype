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