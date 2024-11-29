from rest_framework import serializers
from .models import Device, Fault

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'  # Include all fields in the API

class FaultSerializer(serializers.ModelSerializer):
    device_name = serializers.SerializerMethodField()

    class Meta:
        model = Fault
        fields = ['id', 'time_stamp', 'resolution_time_stamp', 'code', 'duration_seconds', 
                  'device_id', 'asset_id', 'category', 'description', 'fault_type', 'device_name']

    def get_device_name(self, obj):
        # This method calls the device_name method on the Fault model
        return obj.device_name()