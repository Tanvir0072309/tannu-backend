import os
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Student, InstituteSettings
from .serializers import StudentSerializer


def _png_response(data: bytes, filename: str) -> HttpResponse:
    resp = HttpResponse(data, content_type="image/png")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    resp["Content-Length"] = len(data)
    return resp


# ══════════════════════════════════════════════════════════════════════════════
# INSTITUTE SETTINGS  (GET public, PATCH admin)
# ══════════════════════════════════════════════════════════════════════════════

@api_view(["GET"])
def institute_settings(request):
    """
    GET /api/settings/
    Public — home page footer aur stats ke liye.
    Returns: institution, trainer_name, udyam_no, phone, course_rate
    """
    s = InstituteSettings.get()
    return Response({
        "institution":  s.institution,
        "trainer_name": s.trainer_name,
        "udyam_no":     s.udyam_no,
        "phone":        s.phone,
        "course_rate":  s.course_rate,
    })


@api_view(["PATCH"])
def update_settings(request):
    """
    PATCH /api/settings/update/
    Admin — settings DB mein save karo.
    Accepts any subset of: institution, trainer_name, udyam_no, phone, course_rate
    """
    s = InstituteSettings.get()
    allowed = ["institution", "trainer_name", "udyam_no", "phone", "course_rate"]
    for key in allowed:
        if key in request.data:
            setattr(s, key, request.data[key])
    s.save()
    return Response({
        "institution":  s.institution,
        "trainer_name": s.trainer_name,
        "udyam_no":     s.udyam_no,
        "phone":        s.phone,
        "course_rate":  s.course_rate,
    })


# ══════════════════════════════════════════════════════════════════════════════
# CERT NO PREVIEW
# ══════════════════════════════════════════════════════════════════════════════

@api_view(["GET"])
def next_cert_no(request):
    """GET /api/next-cert-no/  — does NOT save, just previews the next number."""
    from django.utils import timezone
    year   = timezone.now().year
    prefix = f"STC-{year}-"
    last   = Student.objects.filter(cert_no__startswith=prefix).order_by("-cert_no").first()
    num    = 1
    if last:
        try:
            num = int(last.cert_no.split("-")[-1]) + 1
        except (ValueError, IndexError):
            pass
    return Response({"cert_no": f"{prefix}{str(num).zfill(3)}"})


# ══════════════════════════════════════════════════════════════════════════════
# STUDENTS
# ══════════════════════════════════════════════════════════════════════════════

@api_view(["GET"])
def student_list(request):
    """GET /api/students/?search=<q>"""
    qs = Student.objects.all()
    q  = request.GET.get("search", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(cert_no__icontains=q))
    return Response(StudentSerializer(qs, many=True).data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def student_create(request):
    """
    POST /api/students/create/
    Multipart form — fields + optional certificate_image file.
    cert_no must be sent (from /api/next-cert-no/ preview).
    """
    data    = request.data.copy()
    cert_no = data.get("cert_no", "").strip()

    if not cert_no:
        return Response({"cert_no": ["cert_no is required."]}, status=400)
    if Student.objects.filter(cert_no=cert_no).exists():
        return Response({"cert_no": [f"{cert_no} already exists. Refresh page."]}, status=400)

    cert_file = request.FILES.get("certificate_image")
    if cert_file:
        from django.conf import settings as djs
        cert_dir  = os.path.join(djs.MEDIA_ROOT, "certificates")
        os.makedirs(cert_dir, exist_ok=True)
        safe_name = (data.get("name", "student") or "student").replace(" ", "_").replace("/", "")
        filename  = f"{cert_no}_{safe_name}.png"
        with open(os.path.join(cert_dir, filename), "wb") as f:
            for chunk in cert_file.chunks():
                f.write(chunk)
        data["certificate_file"] = f"certificates/{filename}"

    s = StudentSerializer(data=data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    student = s.save()
    return Response(StudentSerializer(student).data, status=201)


@api_view(["GET"])
def student_detail(request, pk):
    """GET /api/students/<id>/"""
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(StudentSerializer(student).data)


@api_view(["GET"])
def student_certificate(request, pk):
    """GET /api/students/<id>/certificate/  — download certificate PNG"""
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    from django.conf import settings as djs
    if student.certificate_file:
        fp = os.path.join(djs.MEDIA_ROOT, str(student.certificate_file))
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                raw = f.read()
            safe = student.name.replace(" ", "_").replace("/", "")
            return _png_response(raw, f"{student.cert_no}_{safe}.png")

    return Response({"error": "Certificate image not found. Re-upload."}, status=404)


@api_view(["DELETE"])
def student_delete(request, pk):
    """DELETE /api/students/<id>/delete/"""
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    from django.conf import settings as djs
    if student.certificate_file:
        fp = os.path.join(djs.MEDIA_ROOT, str(student.certificate_file))
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except OSError:
                pass

    student.delete()
    return Response({"deleted": True})


@api_view(["GET"])
def sample_certificate(request):
    """GET /api/sample-certificate/  — home page download button ke liye"""
    from pathlib import Path
    try:
        from django.conf import settings as djs
        base = Path(djs.BASE_DIR)
    except Exception:
        base = Path(__file__).parent.parent

    for name in ["Tannu-certificate-demo.png", "certificate_template.png"]:
        p = base / "tannu_backend" / "assets" / name
        if p.exists():
            return _png_response(p.read_bytes(), "Tannu-Certificate-Sample.png")

    return Response({"error": "Sample not found"}, status=404)


@api_view(["GET"])
def stats(request):
    """GET /api/stats/"""
    total = Student.objects.count()
    paid  = Student.objects.filter(paid=True).count()
    return Response({"total": total, "paid": paid, "pending": total - paid})
