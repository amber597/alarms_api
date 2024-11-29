from django.db import models


class Device(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically handles unique ID
    device_name = models.CharField(max_length=50)  # Device name (String)
    asset = models.CharField(max_length=100)  # Asset name (String)
    asset_id = models.IntegerField()  # Asset ID (Integer)

    def __str__(self):
        return f"{self.device_name}"

class Fault(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically handles unique ID
    time_stamp = models.DateTimeField(db_index=True)  # Timestamp of the event
    resolution_time_stamp = models.DateTimeField()  # Timestamp when the event was resolved
    code = models.IntegerField(db_index=True)  # Event code (Integer)
    duration_seconds = models.FloatField()  # Duration of the event in seconds (Float)
    device_id = models.IntegerField(db_index=True)  # Associated device ID (Integer)
    asset_id = models.IntegerField()  # Associated asset ID (Integer)
    category = models.CharField(max_length=50, blank=True)  # Category of the event (String)
    description = models.TextField(blank=True)  # Description of the event (Text, optional)
    fault_type = models.CharField(max_length=50)  # Type of fault (String)


    def device_name(self):
        try:
            name = Device.objects.get(id=self.device_id).device_name
        except:
            name=''
        return name

    def __str__(self):
        return f"Fault {self.code}"