from django.contrib import admin
from .models import StudyCenter, CustomUser, Course, Certificate, CertificatesSet
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "photo",
                    "phone_number",
                    "is_manager",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class LocationAdmin(admin.ModelAdmin):
    readonly_fields = ("address", "latitude", "longitude")


admin.site.register(StudyCenter, LocationAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(Certificate)
admin.site.register(CertificatesSet)
