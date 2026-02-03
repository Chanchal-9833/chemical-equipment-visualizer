from django.contrib import admin
from .models import UploadHistory

@admin.register(UploadHistory)
class UploadHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'uploaded_at',
        'total_equipment',
        'avg_flowrate',
        'avg_pressure',
        'avg_temperature',
    )
