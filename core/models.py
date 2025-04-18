from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', '病人'),
        ('doctor', '医生'),
        ('admin', '管理员'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class VideoUpload(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    classification_result = models.CharField(max_length=20, blank=True, null=True)


class MIDetection(models.Model):
    video = models.OneToOneField(VideoUpload, on_delete=models.CASCADE)
    model1_result = models.CharField(max_length=20)
    model2_result = models.CharField(max_length=20)
    final_result = models.CharField(max_length=20)
    detected_at = models.DateTimeField(auto_now_add=True)


class Diagnosis(models.Model):
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class DiagnosisHistory(models.Model):
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_content = models.TextField()


class RoleChangeHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    old_role = models.CharField(max_length=10)
    new_role = models.CharField(max_length=10)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_changes')
