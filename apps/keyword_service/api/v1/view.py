from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from apps.keyword_service.models import Keyword
from apps.keyword_service.serializers import KeywordSerializer
from apps.keyword_service.api.v1.swagger_decorator import (
    admin_create_keyword_swagger,
    admin_retrieve_keyword_swagger,
    admin_update_keyword_swagger,
    admin_partial_update_keyword_swagger,
    admin_destroy_keyword_swagger,
    admin_list_keyword_swagger,
    user_retrieve_keyword_swagger,
    user_list_keyword_swagger,
)
from django.db import models

@method_decorator(name='create', decorator=admin_create_keyword_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_keyword_swagger)
@method_decorator(name='update', decorator=admin_update_keyword_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_keyword_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_keyword_swagger)
@method_decorator(name='list', decorator=admin_list_keyword_swagger)
class KeywordAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing Keyword records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = KeywordSerializer
    lookup_field = 'id'
    queryset = Keyword.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['root_keyword', 'keyword', 'keyword_type']


@method_decorator(name='retrieve', decorator=user_retrieve_keyword_swagger)
@method_decorator(name='list', decorator=user_list_keyword_swagger)
class KeywordAPIView(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Authenticated user API ViewSet for viewing own Keyword records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = KeywordSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to keywords associated with projects where the user is the owner or collaborator.
        """
        return Keyword.objects.filter(
            models.Q(project__owner=self.request.user) |
            models.Q(project__collaborators__invitation_receiver=self.request.user, project__collaborators__status='ACCEPT')
        ).distinct()

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve keywords associated with their projects.
        """
        instance = self.get_object()
        if instance.project.owner != self.request.user and not instance.project.collaborators.filter(
            invitation_receiver=self.request.user, status='ACCEPT'
        ).exists():
            raise PermissionDenied(_('You can only access keywords for your own projects or collaborations.'))
        return super().retrieve(request, *args, **kwargs)
