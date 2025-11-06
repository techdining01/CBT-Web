from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from PIL import Image
from exams.models import Class, Subject



class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    GENDER = (
        ('female', 'Female'),
        ('male', 'Male')
        )
  

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    age = models.PositiveIntegerField(default=8)
    date_of_birth = models.CharField(max_length=20, blank=True, null=True)
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, to_field='name', related_name='student_class')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    approved = models.BooleanField(default=False)  # SuperAdmin must approve Admins
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/default_profile.png', null=True, blank=True)
       # NEW FIELDS for teachers/admins
    qualification = models.CharField(max_length=200, blank=True, null=True)
    subject_assigned = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    next_of_kin = models.CharField(max_length=150, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True, null=True)

    def is_teacher(self): 
        return self.role == 'teacher'
    
    def is_student(self): 
        return self.role == 'student'
    
    def can_approve(self):
        """Only SuperAdmins and Admins can approve users"""
        return self.role in ['superadmin', 'admin']
  
    def __str__(self):
        return f"{self.username} ({self.role})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_picture:
            try:
                img = Image.open(self.profile_picture.path)
                # Resize logic
                max_size = (50, 50) 
                img.thumbnail(max_size)

                # Optimize and save
                img.save(self.profile_picture.path, optimize=True, quality=85)
            except Exception:
                pass


class Notification(models.Model):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_sent_notifications"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_notifications"
    )
    message = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_broadcast = models.BooleanField(default=False)  # optional flag
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
 
    def get_target_display(self):
        return f"To {self.recipient} from {self.sender}: {self.message[:30]}"

    def __str__(self):
        return f"To {self.recipient} from {self.sender}: {self.message[:30]}"


class UserStatusLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="status_logs")
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="status_changes")
    changed_at = models.DateTimeField(default=timezone.now)
