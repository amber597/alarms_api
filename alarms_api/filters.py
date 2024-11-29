from django_filters import rest_framework as filters
from .models import Device, Fault

class DeviceFilter(filters.FilterSet):
    asset = filters.CharFilter(lookup_expr='icontains')  # Filter devices by asset name (case-insensitive)
    asset_id = filters.NumberFilter()  # Filter by asset_id

    class Meta:
        model = Device
        fields = ['asset', 'asset_id']  # Expose these fields as filterable

class FaultFilter(filters.FilterSet):
    start_time = filters.DateTimeFilter(field_name="time_stamp", lookup_expr='gte')  # Events after this time
    end_time = filters.DateTimeFilter(field_name="time_stamp", lookup_expr='lte')  # Events before this time
    device_id = filters.NumberFilter()  # Filter by device ID
    code = filters.CharFilter(field_name="code", lookup_expr='exact')

    class Meta:
        model = Fault
        fields = ['fault_type', 'device_id', 'asset_id', 'code']  # Expose these fields as filterable