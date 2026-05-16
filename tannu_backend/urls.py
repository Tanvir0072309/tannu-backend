from django.urls import path
from . import views

urlpatterns = [
    # ── Institute Settings (public GET, admin PATCH) ───────────────────────────
    path("settings/",                      views.institute_settings, name="institute-settings"),
    path("settings/update/",               views.update_settings,    name="update-settings"),

    # ── Students ───────────────────────────────────────────────────────────────
    path("students/",                       views.student_list,        name="student-list"),
    path("students/create/",               views.student_create,      name="student-create"),
    path("students/<int:pk>/",             views.student_detail,      name="student-detail"),
    path("students/<int:pk>/certificate/", views.student_certificate, name="student-certificate"),
    path("students/<int:pk>/delete/",      views.student_delete,      name="student-delete"),

    # ── Utilities ──────────────────────────────────────────────────────────────
    path("next-cert-no/",                  views.next_cert_no,        name="next-cert-no"),
    path("sample-certificate/",            views.sample_certificate,  name="sample-certificate"),
    path("stats/",                         views.stats,               name="stats"),
]
