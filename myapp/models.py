from django.db import models

# Create your models here.
# class LicenseData(models.Model):
#     windows_product_key = models.CharField(max_length=50)
#     license_expiration_date = models.DateTimeField(null=True)
#     mac_address = models.CharField(max_length=17)  # Assuming MAC addresses are stored as strings
#     ip_address = models.GenericIPAddressField()
#     hostname = models.CharField(max_length=255)
#     windows_version = models.CharField(max_length=50)

#     def __str__(self):
#         return f"{self.windows_product_key} - {self.hostname}"