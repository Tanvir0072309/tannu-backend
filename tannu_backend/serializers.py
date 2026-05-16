from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Student
        fields = [
            "id", "cert_no", "name", "phone", "age", "birthdate",
            "village", "district", "start_date", "end_date",
            "fees", "paid", "certificate_file", "created_at",
        ]
        # cert_no is writable: admin sends the previewed value
        read_only_fields = ["id", "created_at"]