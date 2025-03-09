import datetime
from rest_framework import serializers
from .models import StudyCenter, Course, Certificate, CertificatesSet
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class StudyCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCenter
        fields = (
            "id",
            "name",
            "manager",
            "contact_number",
            "location",
        )

    def validate_location(self, value):
        """
        Validate the Google Maps URL and extract latitude and longitude.
        """
        # Regex to extract latitude and longitude from Google Maps URL
        pattern = r"@(-?\d+\.\d+),(-?\d+\.\d+)"
        match = re.search(pattern, value)
        if not match:
            raise serializers.ValidationError(
                "Invalid Google Maps URL. Could not extract latitude and longitude."
            )

        latitude, longitude = match.groups()
        self.context["latitude"] = float(latitude)
        self.context["longitude"] = float(longitude)
        return value

    def validate_contact_number(self, value):
        if not value.isdigit() or len(value) != 12:
            raise serializers.ValidationError("Phone number must be exactly 12 digits.")
        return value

    def validate_manager(self, value):
        if not value.is_manager:
            raise serializers.ValidationError("Manager must have manager privileges.")

        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Name is too long (max 255 characters).")

        return value

    def create(self, validated_data):
        """
        Create a StudyCenter instance and populate latitude and longitude.
        """
        location = validated_data.pop("location")
        latitude = self.context.get("latitude")
        longitude = self.context.get("longitude")

        # Populate the fields
        validated_data["location"] = location
        validated_data["latitude"] = latitude
        validated_data["longitude"] = longitude
        validated_data["address"] = (
            f"Lat: {latitude}, Long: {longitude}"  # Placeholder address
        )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update a StudyCenter instance and populate latitude and longitude.
        """
        location = validated_data.pop("location", None)
        if location:
            latitude = self.context.get("latitude")
            longitude = self.context.get("longitude")

            # Populate the fields
            validated_data["latitude"] = latitude
            validated_data["longitude"] = longitude
            validated_data["address"] = (
                f"Lat: {latitude}, Long: {longitude}"  # Placeholder address
            )

        return super().update(instance, validated_data)

    def __init__(self, *args, **kwargs):
        super(StudyCenterSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request", None)

        if request and request.method == "GET":
            manager = request.GET.get("displayManager", None) == "true"
            if manager:
                self.fields["manager"] = UserSerializer(context=self.context)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "study_center",
            "photo",
            "phone_number",
            "is_manager",
            "is_staff",
        )
        write_only_fields = ("password",)
        read_only_fields = ("is_staff", "is_manager")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name cannot be empty.")
        if len(value) > 50:
            raise serializers.ValidationError(
                "First name is too long (max 50 characters)."
            )
        return value

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be empty.")
        if len(value) > 50:
            raise serializers.ValidationError(
                "Last name is too long (max 50 characters)."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "name",
            "image",
            "type",
            "name_coordinates",
            "id_coordinates",
            "finished_date_coordinates",
            "qr_code_coordinates",
        )

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Name is too long (max 255 characters).")
        return value

    def validate_type(self, value):
        if str(value).lower() not in ["oddiy", "loyiha"]:
            raise serializers.ValidationError("Invalid course type.")
        return value


class CertificatesSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificatesSet
        fields = (
            "id",
            "name",
            "study_center",
            "finished_date",
            "status",
        )

        read_only_fields = ("study_center",)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Name is too long (max 255 characters).")
        return value

    def validate_birthdate(self, value):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise serializers.ValidationError("Invalid date format (YYYY-MM-DD).")
        return value

    def validate_contact_number(self, value):
        if not value.isdigit() or len(value) != 12:
            raise serializers.ValidationError("Phone number must be exactly 12 digits.")
        return value

    def validate_gender(self, value):
        if str(value).lower() not in ["male", "female", "unknown"]:
            raise serializers.ValidationError("Invalid gender.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")

        user_study_center = getattr(request.user, "study_center", None)
        if not user_study_center:
            raise serializers.ValidationError(
                "User is not associated with any study center."
            )

        validated_data["study_center"] = user_study_center
        return super().create(validated_data)

    def __init__(self, *args, **kwargs):
        super(CertificatesSetSerializer, self).__init__(*args, **kwargs)

        request = self.context.get("request", None)
        if request and hasattr(request, "method") and request.method == "GET":
            study_center = request.GET.get("displayStudyCenter", None)
            if study_center:
                self.fields["study_center"] = StudyCenterSerializer(
                    context=self.context
                )


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = (
            "id",
            "UUID",
            "name",
            "social_status",
            "birthdate",
            "contact_number",
            "certificates_set",
            "course",
        )

        read_only_fields = ("id", "UUID")

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate_contact_number(self, value):
        if value and (not value.isdigit() or len(value) != 12):
            raise serializers.ValidationError("Phone number must be exactly 12 digits.")
        return value

    def __init__(self, *args, **kwargs):
        super(CertificateSerializer, self).__init__(*args, **kwargs)
        request = self.context.get("request", None)

        if request and request.method == "GET":
            course = request.GET.get("displayCourse", None) == "true"
            if course:
                self.fields["course"] = CourseSerializer(context=self.context)
