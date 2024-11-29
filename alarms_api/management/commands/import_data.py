import json
from django.core.management.base import BaseCommand
from alarms_api.models import Device, Fault  # Replace `myapp` with your app name

class Command(BaseCommand):
    help = 'Load device and fault data from JSON files into the database'

    def handle(self, *args, **kwargs):
        # Open the JSON file containing device data
        try:
            with open('alarms_api\\fixtures\device.json', 'r') as device_file:
                devices_data = json.load(device_file)
                Device.objects.all().delete()
                for device in devices_data:
                    device_obj = Device.objects.create(
                            id= device['id'],
                            device_name= device['device_name'],
                            asset= device['asset'],
                            asset_id= device['asset_id'],
                    )
                    if device_obj:
                        self.stdout.write(self.style.SUCCESS(f"Successfully added {device['device_name']}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Successfully updated {device['device_name']}"))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('device.json file not found.'))

        # Open the JSON file containing fault data
        try:
            with open('alarms_api\\fixtures\\fault.json', 'r') as fault_file:
                faults_data = json.load(fault_file)
                Fault.objects.all().delete()
                for fault in faults_data:
                    fault_obj = Fault.objects.create(
                            time_stamp=fault['time_stamp'],
                            resolution_time_stamp=fault['resolution_time_stamp'],
                            code=fault['code'],
                            duration_seconds=fault['duration_seconds'],
                            device_id=fault['device_id'],
                            asset_id=fault['asset_id'],
                            category=fault['category'],
                            description=fault['description'],
                            fault_type=fault['fault_type'],
                        )
                    if fault_obj:
                        self.stdout.write(self.style.SUCCESS(f"Successfully added Fault {fault_obj.id}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Successfully updated Fault {fault_obj.id}"))
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR('fault.json file not found.'))
