from rest_framework import generics
from .models import Device, Fault
from .serializers import DeviceSerializer, FaultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum


from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Sum
from .models import Fault, Device
from .serializers import FaultSerializer

from django.db.models import Sum, Max


class FaultListView(generics.ListAPIView):
    queryset = Fault.objects.all()
    serializer_class = FaultSerializer

    # Apply filters based on query parameters
    def filter_query_params(self, qs, query_params):
        if query_params:
            if 'state' in query_params:
                device_ids = Device.objects.filter(asset__in=query_params['state'].split(',')).values_list('id', flat=True)
                qs = qs.filter(device_id__in=device_ids)
            if 'device' in query_params:
                device_ids = Device.objects.filter(device_name__in=query_params['device'].split(',')).values_list('id', flat=True)
                qs = qs.filter(device_id__in=device_ids)
            if 'fault' in query_params:
                qs = qs.filter(fault_type__in=query_params['fault'].split(','))
            if 'code' in query_params:
                qs = qs.filter(code__in=query_params['code'].split(','))
            if 'start_time' in query_params:
                qs = qs.filter(time_stamp__gte=query_params['start_time'])
            if 'end_time' in query_params:
                qs = qs.filter(time_stamp__lte=query_params['end_time'])
        return qs  # Ensure the filtered queryset is returned

    def get_overview_data(self,qs):
        # Initialize result dictionary with default values
        res = {
            'total_duration': 0,
            'total_alarms': 0,
            'device_max_duration': '',
            'max_duration_alarm_time': 0,
        }

        # Aggregate the queryset to compute total and max values
        qs_aggregates = qs.aggregate(
            total_duration=Sum('duration_seconds'),
            total_alarms=Sum('id'),
            max_duration_alarm_time=Max('duration_seconds')
        )

        # Retrieve the maximum duration
        max_duration_alarm_time = qs_aggregates.get('max_duration_alarm_time')
        
        # Find the device associated with the maximum duration
        device_id = None
        if max_duration_alarm_time is not None:
            max_duration_entry = qs.filter(duration_seconds=max_duration_alarm_time).first()
            if max_duration_entry:
                device_id = max_duration_entry.device_id

        # Attempt to fetch the device name if the ID is found
        if device_id:
            try:
                res['device_max_duration'] = Device.objects.get(id=device_id).device_name
            except Device.DoesNotExist:
                res['device_max_duration'] = ''
            
        def format_duration(seconds):
            # Use divmod to calculate hours, minutes, and remaining seconds
            hours, remainder = divmod(int(seconds), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02} hrs, {minutes:02} min, {seconds:02} sec"

        # Update result dictionary with aggregated values
        res['total_duration'] = format_duration(qs_aggregates.get('total_duration', 0))
        res['total_alarms'] = qs_aggregates.get('total_alarms', 0)
        res['max_duration_alarm_time'] = format_duration(max_duration_alarm_time or 0)

        return res


    # Get device-specific data (top 10 by duration or frequency)
    def get_device_data(self, qs):
        def get_query_data(qs, column=None):
            top_devices = (
                qs.values('device_id')
                .annotate(value=Sum(column))
                .order_by('-value')[:10]
            )
            for device in top_devices:
                if column == 'duration_seconds':
                    device['value'] = device['value']/3600
                try:
                    device['label'] = Device.objects.get(id=device['device_id']).device_name
                except Device.DoesNotExist:
                    device['label'] = ''        
            return top_devices
        
        return {
            'duration': get_query_data(qs, 'duration_seconds'),
            'frequency': get_query_data(qs, 'id')  # Frequency can be counted by 'id'
        }

    # Get category-specific data (total duration and frequency)
    def get_category_data(self, qs):
        def get_query_data(qs, column):
            res =  [{'value': obj['value'], 'label': obj['category']}  for obj in qs.values('category').annotate(value=Sum(column))]
            if column == 'duration_seconds':
                for obj in res:
                    obj['value'] = obj['value']/3600
            return res
        
        return {
            'duration': get_query_data(qs, 'duration_seconds'),
            'frequency': get_query_data(qs, 'id')
        }

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()  # Start with the full queryset
        query_params = request.query_params  # Access query parameters from the request

        # Apply filters
        qs = self.filter_query_params(qs, query_params)

        # Fetch additional device and category data
        device_data = self.get_device_data(qs)
        category_data = self.get_category_data(qs)
        overview_data = self.get_overview_data(qs)

        # Serialize the main queryset (Fault objects)
        serializer = self.get_serializer(qs, many=True)

        # Return the serialized data along with additional data in the response
        return Response({
            'faults': serializer.data,  # Main fault data
            'device_data': device_data,  # Top devices data
            'category_data': category_data , # Category data
            'overview_data': overview_data,
        })





@api_view(['GET'])
def filters_list(request):
    # Fetch distinct values for each filter, prepend 'All' as an option
    filter_options = {
        'states': Device.objects.values_list('asset', flat=True).distinct(),
        'devices': Device.objects.values_list('device_name', flat=True).distinct(),
        'fault_types': Fault.objects.values_list('fault_type', flat=True).distinct(),
        'codes': Fault.objects.values_list('code', flat=True).distinct(),
    }
    return Response(filter_options)