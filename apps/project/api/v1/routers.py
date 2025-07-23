from rest_framework.routers import DefaultRouter
from apps.project.api.v1.view import (
    ProjectAdminAPIView,
    ProjectAPIView,
    ProcessAdminAPIView,
    ProcessAPIView,
)

router = DefaultRouter()
router.register(r'admin/projects', ProjectAdminAPIView, basename='admin-project')
router.register(r'projects', ProjectAPIView, basename='project')
router.register(r'admin/processes', ProcessAdminAPIView, basename='admin-process')
router.register(r'processes', ProcessAPIView, basename='process')

urlpatterns = router.urls
