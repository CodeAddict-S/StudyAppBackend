from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response, status
from rest_framework.decorators import api_view
from .models import (
    StudyCenter,
    CustomUser,
    Course,
    Certificate,
    CertificatesSet,
)
from .serializers import (
    StudyCenterSerializer,
    UserSerializer,
    CertificateSerializer,
    CourseSerializer,
    CertificatesSetSerializer,
)
from .cerificate_generator import Certificates

frontend_url = "https://study-app.ucrm.uz"


# Create your views here.
class StudyCenterViewSet(viewsets.ModelViewSet):
    queryset = StudyCenter.objects.filter(active=True)
    serializer_class = StudyCenterSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ("is_manager",)

    @action(detail=False, methods=["get"], url_path="me")
    def get_me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class CertificatesViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.filter(active=True)
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = "__all__"


class CertificatesSetViewSet(viewsets.ModelViewSet):
    serializer_class = CertificatesSetSerializer
    permission_classes = [IsAuthenticated]
    queryset = CertificatesSet.objects.none()
    filterset_fields = "__all__"

    def get_queryset(self):
        queryset = CertificatesSet.objects.filter(active=True)
        request = self.request
        # Filtering by status
        status_param = request.GET.get("displayStatus")
        if status_param:
            statuses = status_param.split(",")
            queryset = queryset.filter(status__in=statuses)
        if self.request.user.is_manager:
            queryset = queryset.filter(study_center=self.request.user.study_center)
        return queryset

    @action(methods=["GET"], detail=True)
    def generate_zip(self, request, pk=None):
        instance = self.get_object()

        data = {
            "zip_name": instance.name,
            "certificates": [
                {
                    "bg_image_path": (
                        instance.certificates.first().course.image.path
                        if instance.certificates.exists()
                        else ""
                    ),
                    "name": certificate.name,
                    "qrcode": {
                        "url": f"{frontend_url}/certificate/{certificate.UUID}",
                        "x": certificate.course.qr_code_coordinates["x"],
                        "y": certificate.course.qr_code_coordinates["y"],
                        "size": certificate.course.qr_code_coordinates["size"],
                    },
                    "texts": [
                        {
                            "content": certificate.name,
                            "x": certificate.course.name_coordinates["x"],
                            "y": certificate.course.name_coordinates["y"],
                            "size": certificate.course.name_coordinates["size"],
                        },
                        {
                            "content": certificate.UUID,
                            "x": certificate.course.id_coordinates["x"],
                            "y": certificate.course.id_coordinates["y"],
                            "size": certificate.course.id_coordinates["size"],
                        },
                        {
                            "content": instance.finished_date.strftime("%d.%m.%Y"),
                            "x": certificate.course.finished_date_coordinates["x"],
                            "y": certificate.course.finished_date_coordinates["y"],
                            "size": certificate.course.finished_date_coordinates[
                                "size"
                            ],
                        },
                    ],
                }
                for certificate in instance.certificates.all()
            ],
        }
        
        # Generate zip in memory
        try:
            zip_data = Certificates.generate_many_certificates(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
    
        response = HttpResponse(zip_data, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{data["zip_name"]}.zip"'
        return response


@api_view(["GET"])
def certificate_by_uuid(request, uuid):
    if uuid:
        try:
            certificate = Certificate.objects.get(UUID=uuid)
            serializer = CertificateSerializer(certificate)

            # Add the certificate URL to the response data
            response_data = serializer.data
            certificate_set = CertificatesSet.objects.filter(
                certificates__in=[certificate]
            ).first()
            response_data["course"] = CourseSerializer(certificate.course).data
            response_data["certificates_set"] = CertificatesSetSerializer(
                certificate_set
            ).data
            response_data["study_center"] = StudyCenterSerializer(
                certificate_set.study_center
            ).data["name"]

            return Response(response_data)
        except Certificate.DoesNotExist:
            return Response(
                {"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            {"error": "UUID is required"}, status=status.HTTP_400_BAD_REQUEST
        )
