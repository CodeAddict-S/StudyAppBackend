from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
import uuid


def generate_short_uuid():
    return f"ID{str(uuid.uuid4().int)[:5]}"


class StudyCenter(models.Model):
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    manager = models.OneToOneField(
        "CustomUser", on_delete=models.SET_NULL, null=True, blank=True
    )
    contact_number = models.CharField(max_length=12, null=True, blank=True)
    location = models.URLField(max_length=500)
    address = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def save(self, *args, **kwargs):
        # Get the previous manager before saving
        if self.pk:
            old_manager = (
                StudyCenter.objects.filter(pk=self.pk)
                .values_list("manager_id", flat=True)
                .first()
            )
        else:
            old_manager = None

        super().save(*args, **kwargs)

        # If there was a previous manager, clear their study_center field
        if old_manager and old_manager != self.manager_id:
            CustomUser.objects.filter(pk=old_manager).update(study_center=None)

        if self.manager:
            self.manager.study_center = self
            self.manager.save(update_fields=["study_center"])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "O'quv Markaz"
        verbose_name_plural = "O'quv Markazlari"


class CustomUser(AbstractUser):
    email = None
    photo = models.FileField(null=True, blank=True)
    phone_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    is_manager = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    study_center = models.ForeignKey(
        "StudyCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managers",
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.first_name + " " + self.last_name

    def save(self, *args, **kwargs):
        if self.is_staff:
            self.is_manager = False

        return super().save(*args, **kwargs)


class Course(models.Model):
    PROJECT_CHOICES = [
        ("oddiy", "Oddiy"),
        ("loyiha", "Loyiha"),
    ]
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    type = models.CharField(max_length=10, choices=PROJECT_CHOICES, default="oddiy")
    image = models.ImageField(upload_to="courses", null=False, blank=False)
    name_coordinates = models.JSONField(null=True, blank=True)
    id_coordinates = models.JSONField(null=True, blank=True)
    finished_date_coordinates = models.JSONField(null=True, blank=True)
    qr_code_coordinates = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"


class CertificatesSet(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    study_center = models.ForeignKey(
        StudyCenter, related_name="general_sets", on_delete=models.CASCADE
    )
    finished_date = models.DateField()
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=10,
        default="draft",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Certificates set"
        verbose_name_plural = "Certificates sets"


class Certificate(models.Model):
    UUID = models.CharField(
        max_length=7, unique=True, default=generate_short_uuid, editable=False
    )
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    birthdate = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=12, null=True, blank=True)
    social_status = models.CharField(max_length=100, null=True, blank=True)
    certificates_set = models.ForeignKey(
        CertificatesSet, related_name="certificates", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"
