from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from apps.project.models import Project, Process
from apps.project.serializers import ProjectSerializer, ProcessSerializer
from apps.project.api.v1.swagger_decorator import (
    admin_create_project_swagger,
    admin_retrieve_project_swagger,
    admin_update_project_swagger,
    admin_partial_update_project_swagger,
    admin_destroy_project_swagger,
    admin_list_project_swagger,
    user_create_project_swagger,
    user_retrieve_project_swagger,
    user_update_project_swagger,
    user_partial_update_project_swagger,
    user_destroy_project_swagger,
    user_list_project_swagger,
    admin_create_process_swagger,
    admin_retrieve_process_swagger,
    admin_update_process_swagger,
    admin_partial_update_process_swagger,
    admin_destroy_process_swagger,
    admin_list_process_swagger,
    user_retrieve_process_swagger,
    user_list_process_swagger,
    user_list_project_processes_swagger,
)

@method_decorator(name='create', decorator=admin_create_project_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_project_swagger)
@method_decorator(name='update', decorator=admin_update_project_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_project_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_project_swagger)
@method_decorator(name='list', decorator=admin_list_project_swagger)
class ProjectAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing Project records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = ProjectSerializer
    lookup_field = 'id'
    queryset = Project.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'owner__username']

@method_decorator(name='create', decorator=user_create_project_swagger)
@method_decorator(name='retrieve', decorator=user_retrieve_project_swagger)
@method_decorator(name='update', decorator=user_update_project_swagger)
@method_decorator(name='partial_update', decorator=user_partial_update_project_swagger)
@method_decorator(name='destroy', decorator=user_destroy_project_swagger)
@method_decorator(name='list', decorator=user_list_project_swagger)
class ProjectAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Authenticated user API ViewSet for managing own Project records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to projects where the user is the owner or a collaborator.
        """
        return Project.objects.filter(
            models.Q(owner=self.request.user) |
            models.Q(collaborators__invitation_receiver=self.request.user, collaborators__status='ACCEPT')
        ).distinct()

    def create(self, request, *args, **kwargs):
        """
        Set owner to authenticated user and prevent modification of owner field.
        """
        if 'owner_id' in request.data and request.data['owner_id'] != self.request.user.id:
            raise ValidationError(_('Owner must be the authenticated user.'))
        request.data['owner_id'] = self.request.user.id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Ensure user can only update their own projects or those they collaborate on.
        """
        instance = self.get_object()
        if instance.owner != self.request.user and not instance.collaborators.filter(
            invitation_receiver=self.request.user, status='ACCEPT'
        ).exists():
            raise PermissionDenied(_('You can only update your own projects or those you collaborate on.'))
        if 'owner_id' in request.data:
            raise ValidationError(_('Owner field cannot be modified.'))
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Ensure user can only partially update their own projects or those they collaborate on.
        """
        instance = self.get_object()
        if instance.owner != self.request.user and not instance.collaborators.filter(
            invitation_receiver=self.request.user, status='ACCEPT'
        ).exists():
            raise PermissionDenied(_('You can only update your own projects or those you collaborate on.'))
        if 'owner_id' in request.data:
            raise ValidationError(_('Owner field cannot be modified.'))
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Ensure user can only delete their own projects.
        """
        instance = self.get_object()
        if instance.owner != self.request.user:
            raise PermissionDenied(_('You can only delete your own projects.'))
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve their own projects or those they collaborate on.
        """
        instance = self.get_object()
        if instance.owner != self.request.user and not instance.collaborators.filter(
            invitation_receiver=self.request.user, status='ACCEPT'
        ).exists():
            raise PermissionDenied(_('You can only access your own projects or those you collaborate on.'))
        return super().retrieve(request, *args, **kwargs)

@method_decorator(name='create', decorator=admin_create_process_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_process_swagger)
@method_decorator(name='update', decorator=admin_update_process_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_process_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_process_swagger)
@method_decorator(name='list', decorator=admin_list_process_swagger)
class ProcessAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing Process records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = ProcessSerializer
    lookup_field = 'id'
    queryset = Process.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['project__name', 'status']

@method_decorator(name='retrieve', decorator=user_retrieve_process_swagger)
@method_decorator(name='list', decorator=user_list_process_swagger)
@method_decorator(name='list_project_processes', decorator=user_list_project_processes_swagger)
class ProcessAPIView(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Authenticated user API ViewSet for viewing Process records for accessible projects.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProcessSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to active processes for projects where the user is the owner or collaborator.
        """
        return Process.objects.filter(
            models.Q(project__owner=self.request.user) |
            models.Q(project__collaborators__invitation_receiver=self.request.user, project__collaborators__status='ACCEPT'),
            status__in=['pending', 'started']
        ).distinct()

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve processes for their own projects or collaborations.
        """
        instance = self.get_object()
        if instance.project.owner != self.request.user and not instance.project.collaborators.filter(
            invitation_receiver=self.request.user, status='ACCEPT'
        ).exists():
            raise PermissionDenied(_('You can only access processes for your own projects or collaborations.'))
        if instance.status == 'finished':
            raise PermissionDenied(_('You cannot access finished processes.'))
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='project/(?P<project_id>\d+)')
    def list_project_processes(self, request, project_id=None):
        """
        List all active processes for a specific project where the user is the owner or collaborator.
        """
        try:
            project = Project.objects.get(id=project_id)
            if project.owner != self.request.user and not project.collaborators.filter(
                invitation_receiver=self.request.user, status='ACCEPT'
            ).exists():
                raise PermissionDenied(_('You can only access processes for your own projects or collaborations.'))
            processes = Process.objects.filter(project=project, status__in=['pending', 'started'])
            serializer = self.get_serializer(processes, many=True)
            return Response(serializer.data)
        except Project.DoesNotExist:
            raise ValidationError(_('Project with the specified ID does not exist.'))
