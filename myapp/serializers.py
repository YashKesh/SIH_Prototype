
from rest_framework import serializers
from .models import WindowsInformation


class WindowsInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WindowsInformation
        fields = '__all__'
        
from rest_framework import serializers
from .models import SystemUsage

class SystemUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUsage
        fields = '__all__'
