from django import forms
from .models import Firewall

# forms.py
class FirewallForm(forms.ModelForm):
    class Meta:
        model = Firewall
        fields = ['name', 'ip', 'port', 'location', 'description']
        
# forms.py

from django import forms

class LogUploadForm(forms.Form):
    log_file = forms.FileField()
