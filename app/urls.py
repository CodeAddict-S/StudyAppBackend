from rest_framework import routers
from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register("study-centers", StudyCenterViewSet)
router.register("users", UserViewSet)
router.register("courses", CourseViewSet)
router.register("certificate-sets", CertificatesSetViewSet)
router.register("certificates", CertificatesViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "get-certificate/<str:uuid>/", certificate_by_uuid, name="get_certificate"
    ),
]
