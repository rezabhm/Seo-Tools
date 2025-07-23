from rest_framework.routers import DefaultRouter
from apps.keyword_service.api.v1.view import (
    KeywordAdminAPIView,
    KeywordAPIView,
)

router = DefaultRouter()
router.register(r'admin/keywords', KeywordAdminAPIView, basename='admin-keyword')
router.register(r'keywords', KeywordAPIView, basename='keyword')

urlpatterns = router.urls
