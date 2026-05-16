from django.db import models
from django.utils import timezone


def _next_cert_no():
    """Auto-generate STC-YYYY-NNN format certificate number."""
    year = timezone.now().year
    prefix = f"STC-{year}-"
    last = (
        Student.objects.filter(cert_no__startswith=prefix)
        .order_by("-cert_no")
        .first()
    )
    num = 1
    if last:
        try:
            num = int(last.cert_no.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    return f"{prefix}{str(num).zfill(3)}"


class Student(models.Model):
    cert_no          = models.CharField(max_length=30, unique=True, blank=True)
    name             = models.CharField(max_length=200)
    phone            = models.CharField(max_length=20, blank=True)
    age              = models.CharField(max_length=5, blank=True)
    birthdate        = models.DateField(null=True, blank=True)
    village          = models.CharField(max_length=100, blank=True)
    district         = models.CharField(max_length=100, blank=True)
    start_date       = models.DateField(null=True, blank=True)
    end_date         = models.DateField(null=True, blank=True)
    fees             = models.CharField(max_length=20, blank=True, default="499")
    paid             = models.BooleanField(default=False)
    certificate_file = models.CharField(max_length=300, blank=True)  # relative path in MEDIA_ROOT
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.cert_no:
            self.cert_no = _next_cert_no()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cert_no} — {self.name}"


class InstituteSettings(models.Model):
    """Singleton model to store institute configuration in DB."""
    institution   = models.CharField(max_length=200, default="Tannu Tailoring & Fashion Classes")
    trainer_name  = models.CharField(max_length=100, default="Tanisha Pathan")
    udyam_no      = models.CharField(max_length=50,  default="UDYAM-GJ-XXXXXXXX")
    phone         = models.CharField(max_length=20,  blank=True, default="")
    course_rate   = models.CharField(max_length=20,  default="499")
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Institute Settings"
        verbose_name_plural = "Institute Settings"

    def __str__(self):
        return f"Settings — {self.institution}"

    @classmethod
    def get(cls):
        """Always return the single settings row, creating it if missing."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj