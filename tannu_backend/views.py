import os
import cloudinary
import cloudinary.uploader
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Student, InstituteSettings
from .serializers import StudentSerializer

# ── Cloudinary config — settings.py se auto-configure hoga ───────────────────
cloudinary.config(
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key    = os.environ.get("CLOUDINARY_API_KEY",    ""),
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", ""),
    secure     = True,
)


def _png_response(data: bytes, filename: str) -> HttpResponse:
    resp = HttpResponse(data, content_type="image/png")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    resp["Content-Length"] = len(data)
    return resp


# ══════════════════════════════════════════════════════════════════════════════
# INSTITUTE SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

@api_view(["GET"])
def institute_settings(request):
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
    s = InstituteSettings.get()
    for key in ["institution", "trainer_name", "udyam_no", "phone", "course_rate"]:
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
    Certificate image → Cloudinary par upload → URL database mein save.
    """
    data    = request.data.copy()
    cert_no = data.get("cert_no", "").strip()

    if not cert_no:
        return Response({"cert_no": ["cert_no is required."]}, status=400)
    if Student.objects.filter(cert_no=cert_no).exists():
        return Response({"cert_no": [f"{cert_no} already exists. Refresh."]}, status=400)

    cert_file = request.FILES.get("certificate_image")
    if cert_file:
        try:
            safe_name = (data.get("name", "student") or "student") \
                        .replace(" ", "_").replace("/", "")
            public_id = f"tannu_certificates/{cert_no}_{safe_name}"

            # Cloudinary par upload — permanent URL milega
            result = cloudinary.uploader.upload(
                cert_file,
                public_id   = public_id,
                overwrite   = True,
                resource_type = "image",
                format      = "png",
            )
            # secure_url = "https://res.cloudinary.com/..."
            data["certificate_file"] = result["secure_url"]

        except Exception as e:
            return Response(
                {"certificate_image": [f"Upload failed: {str(e)}"]},
                status=400
            )

    s = StudentSerializer(data=data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    student = s.save()
    return Response(StudentSerializer(student).data, status=201)


@api_view(["GET"])
def student_detail(request, pk):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    return Response(StudentSerializer(student).data)


@api_view(["GET"])
def student_certificate(request, pk):
    """Download certificate — Cloudinary URL se redirect karo."""
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    if not student.certificate_file:
        return Response({"error": "No certificate uploaded."}, status=404)

    cert_url = student.certificate_file

    # Agar Cloudinary URL hai — redirect karo
    if cert_url.startswith("http"):
        from django.shortcuts import redirect
        return redirect(cert_url)

    # Fallback: local file (development)
    from django.conf import settings as djs
    fp = os.path.join(djs.MEDIA_ROOT, str(cert_url))
    if os.path.exists(fp):
        with open(fp, "rb") as f:
            raw = f.read()
        safe = student.name.replace(" ", "_").replace("/", "")
        return _png_response(raw, f"{student.cert_no}_{safe}.png")

    return Response({"error": "Certificate not found."}, status=404)


@api_view(["DELETE"])
def student_delete(request, pk):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    # Cloudinary se bhi delete karo
    if student.certificate_file and student.certificate_file.startswith("http"):
        try:
            # public_id extract karo URL se
            # URL format: https://res.cloudinary.com/<cloud>/image/upload/v123/tannu_certificates/STC-...
            parts = student.certificate_file.split("/upload/")
            if len(parts) == 2:
                # version hata ke public_id nikalo
                pid_part = parts[1]
                # "v1234567/tannu_certificates/STC-2026-001_Name.png"
                pid_no_version = "/".join(pid_part.split("/")[1:])  # version remove
                public_id = pid_no_version.rsplit(".", 1)[0]       # .png remove
                cloudinary.uploader.destroy(public_id)
        except Exception:
            pass  # delete fail ho to bhi student record delete karo

    # Local file fallback
    elif student.certificate_file:
        from django.conf import settings as djs
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
    total = Student.objects.count()
    paid  = Student.objects.filter(paid=True).count()
    return Response({"total": total, "paid": paid, "pending": total - paid})