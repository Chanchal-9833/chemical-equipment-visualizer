from django.urls import path
from .views import equipment_list, upload_csv, upload_history, equipment_summary ,filter_equipment
from .views import equipment_by_upload,generate_report

urlpatterns = [
    path('upload-csv/', upload_csv),
     path('history/', upload_history),
     path('equipment/', equipment_list),
     path('summary/', equipment_summary),
      path("filter-equipment/", filter_equipment),
       path("uploads/", upload_history),
       path("equipment-by-upload/<int:upload_id>/", equipment_by_upload),
       path("report/", generate_report),

]

