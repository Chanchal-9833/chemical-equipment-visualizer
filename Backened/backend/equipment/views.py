from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from .models import UploadHistory,Equipment
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Equipment,UploadHistory



@api_view(['POST'])
def upload_csv(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file uploaded"}, status=400)

    file = request.FILES['file']

    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    total_count = len(df)

    avg_flowrate = df["Flowrate"].mean()
    avg_pressure = df["Pressure"].mean()
    avg_temperature = df["Temperature"].mean()

    type_distribution = df["Type"].value_counts().to_dict()

    upload = UploadHistory.objects.create(
    total_equipment=len(df),
    avg_flowrate=df['Flowrate'].mean(),
    avg_pressure=df['Pressure'].mean(),
    avg_temperature=df['Temperature'].mean(),
    type_distribution=df['Type'].value_counts().to_dict()
)

    for _, row in df.iterrows():
        Equipment.objects.create(
        upload=upload,
        equipment_name=row['Equipment Name'],
        equipment_type=row['Type'],
        flowrate=row['Flowrate'],
        pressure=row['Pressure'],
        temperature=row['Temperature']
    )
    return Response({
        "message": "CSV uploaded successfully",
        "upload_id": upload.id
    })


@api_view(['GET'])
def upload_history(request):
    history = UploadHistory.objects.order_by('-uploaded_at')[:5]

    data = []
    for item in history:
        data.append({
            "id": item.id,
            "uploaded_at": item.uploaded_at,
            "total_equipment": item.total_equipment,
            "avg_flowrate": item.avg_flowrate,
            "avg_pressure": item.avg_pressure,
            "avg_temperature": item.avg_temperature,
            "type_distribution": item.type_distribution
        })

    return Response(data)


@api_view(['GET'])
def equipment_list(request):
    data = Equipment.objects.all().values()
    return Response(data)





@api_view(['GET'])
def equipment_summary(request):
    upload_id = request.GET.get("upload_id")

    qs = Equipment.objects.all()
    if upload_id:
        qs = qs.filter(upload_id=upload_id)

    total = qs.count()

    data = {
        "summary": {
            "total_equipment": total,
            "avg_flowrate": qs.aggregate(Avg("flowrate"))["flowrate__avg"] or 0,
            "avg_pressure": qs.aggregate(Avg("pressure"))["pressure__avg"] or 0,
            "avg_temperature": qs.aggregate(Avg("temperature"))["temperature__avg"] or 0,
        },
        "type_distribution": list(
            qs.values("equipment_type")
              .annotate(count=Count("id"))
        )
    }

    return JsonResponse(data)



def filter_equipment(request):
    upload_id = request.GET.get("upload_id")
    equipment_type = request.GET.get("type")

    qs = Equipment.objects.all()

    if upload_id:
        qs = qs.filter(upload_id=upload_id)

    if equipment_type:
        qs = qs.filter(equipment_type=equipment_type)

    data = []
    for e in qs:
        data.append({
            "equipment_name": e.equipment_name,
            "equipment_type": e.equipment_type,
            "flowrate": e.flowrate,
            "pressure": e.pressure,
            "temperature": e.temperature,
        })

    return JsonResponse(data, safe=False)

def upload_history(request):
    uploads = UploadHistory.objects.order_by('-uploaded_at')[:5]

    data = []
    for u in uploads:
        data.append({
            "id": u.id,
            "uploaded_at": u.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "total_equipment": u.total_equipment
        })

    return JsonResponse(data, safe=False)

def equipment_by_upload(request, upload_id):
    equipments = Equipment.objects.filter(upload_id=upload_id)

    data = []
    for e in equipments:
        data.append({
            "equipment_name": e.equipment_name,
            "equipment_type": e.equipment_type,
            "flowrate": e.flowrate,
            "pressure": e.pressure,
            "temperature": e.temperature,
        })

    return JsonResponse(data, safe=False)


from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import UploadHistory, Equipment


def generate_report(request):
    upload_id = request.GET.get("upload_id")

    if not upload_id:
        return JsonResponse({"error": "upload_id required"}, status=400)

    # ✅ FIX 1: Correct MODEL passed
    upload = get_object_or_404(UploadHistory, id=upload_id)

    equipment = Equipment.objects.filter(upload=upload)

    summary = equipment.aggregate(
        avg_flowrate=Avg("flowrate"),
        avg_pressure=Avg("pressure"),
        avg_temperature=Avg("temperature"),
        total=Count("id")
    )

    type_distribution = (
        equipment.values("equipment_type")
        .annotate(count=Count("id"))
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="report_upload_{upload_id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    # ---------- TITLE ----------
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Chemical Equipment Report")
    y -= 30

    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Upload ID: {upload.id}")
    y -= 20
    p.drawString(50, y, f"Uploaded At: {upload.uploaded_at}")
    y -= 30

    # ---------- SUMMARY ----------
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Summary")
    y -= 20

    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Total Equipment: {summary['total']}")
    y -= 15

    p.drawString(
        50, y,
        f"Avg Flowrate: {(summary['avg_flowrate'] or 0):.2f}"
    )
    y -= 15

    p.drawString(
        50, y,
        f"Avg Pressure: {(summary['avg_pressure'] or 0):.2f}"
    )
    y -= 15

    p.drawString(
        50, y,
        f"Avg Temperature: {(summary['avg_temperature'] or 0):.2f}"
    )
    y -= 30

    # ---------- TYPE DISTRIBUTION ----------
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Equipment Type Distribution")
    y -= 20

    p.setFont("Helvetica", 11)
    for t in type_distribution:
        p.drawString(
            50, y,
            f"{t['equipment_type']} : {t['count']}"
        )
        y -= 15

    y -= 20

    # ---------- EQUIPMENT LIST ----------
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Equipment List")
    y -= 20

    p.setFont("Helvetica", 10)
    for e in equipment:
        line = (
            f"{e.equipment_name} | {e.equipment_type} | "
            f"F:{e.flowrate} | P:{e.pressure} | T:{e.temperature}"
        )
        p.drawString(50, y, line)
        y -= 12

        if y < 50:
            p.showPage()
            y = height - 50

    p.save()
    return response


