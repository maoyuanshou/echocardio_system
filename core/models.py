from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class VideoUpload(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    upload_time = models.DateTimeField(auto_now_add=True)
    classification_result = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.patient.username} - {self.video.name}"


class MIDetection(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE)
    result_model1 = models.CharField(max_length=10)
    result_model2 = models.CharField(max_length=10)
    final_result = models.CharField(max_length=10)  # "MI" or "Normal"
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.final_result}"


class Diagnosis(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_diagnoses')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_diagnoses')
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE)
    diagnosis_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor.username}'s diagnosis of {self.patient.username}"


class DiagnosisHistory(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_content = models.TextField()


class RoleChangeHistory(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_role_changes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_role_changes')
    old_role = models.CharField(max_length=50)
    new_role = models.CharField(max_length=50)
    change_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} changed {self.user.username}'s role"
