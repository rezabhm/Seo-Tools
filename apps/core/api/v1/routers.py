from rest_framework.routers import DefaultRouter
from apps.core.api.v1.views import (
    CustomUserAdminAPIView,
    CustomUserAPIView,
)

router = DefaultRouter()
router.register(r'admin/users', CustomUserAdminAPIView, basename='admin-user')
router.register(r'users', CustomUserAPIView, basename='user')

urlpatterns = router.urls
