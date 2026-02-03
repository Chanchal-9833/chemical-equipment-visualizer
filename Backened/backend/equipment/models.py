from django.db import models

class UploadHistory(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_equipment = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    type_distribution = models.JSONField()

    def __str__(self):
        return f"Upload {self.id} - {self.uploaded_at}"


class Equipment(models.Model):
    upload = models.ForeignKey(
        UploadHistory,
        on_delete=models.CASCADE,
        related_name="equipments"
    )
    equipment_name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()

    def __str__(self):
        return self.equipment_name
    
class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Upload {self.id}"