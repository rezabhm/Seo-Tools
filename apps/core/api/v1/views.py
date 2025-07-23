from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.models import CustomUser, Collaborator
from apps.core.serializers import CustomUserSerializer, CollaboratorSerializer
from apps.core.api.v1.swagger_decorator import (
    admin_create_user_swagger,
    admin_retrieve_user_swagger,
    admin_update_user_swagger,
    admin_partial_update_user_swagger,
    admin_destroy_user_swagger,
    admin_list_user_swagger,
    public_create_user_swagger,
    user_retrieve_user_swagger,
    user_update_user_swagger,
    user_partial_update_user_swagger,
    admin_create_collaborator_swagger,
    admin_retrieve_collaborator_swagger,
    admin_update_collaborator_swagger,
    admin_partial_update_collaborator_swagger,
    admin_destroy_collaborator_swagger,
    admin_list_collaborator_swagger,
    user_create_collaborator_swagger,
    user_retrieve_collaborator_swagger,
    user_update_collaborator_swagger,
    user_partial_update_collaborator_swagger,
    user_destroy_collaborator_swagger,
    user_list_collaborator_swagger,
    user_list_received_invitations_swagger,
    user_handle_invitation_swagger,
)


@method_decorator(name='create', decorator=admin_create_user_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_user_swagger)
@method_decorator(name='update', decorator=admin_update_user_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_user_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_user_swagger)
@method_decorator(name='list', decorator=admin_list_user_swagger)
class CustomUserAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing CustomUser records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = CustomUserSerializer
    lookup_field = 'id'
    queryset = CustomUser.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']


@method_decorator(name='create', decorator=public_create_user_swagger)
class CustomUserPublicAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
):
    """
    Public API ViewSet for creating CustomUser records.
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


@method_decorator(name='retrieve', decorator=user_retrieve_user_swagger)
@method_decorator(name='update', decorator=user_update_user_swagger)
@method_decorator(name='partial_update', decorator=user_partial_update_user_swagger)
class CustomUserAPIView(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Authenticated user API ViewSet for managing own CustomUser record.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to the authenticated user's record.
        """
        return CustomUser.objects.filter(id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure the user can only retrieve their own record.
        """
        instance = self.get_object()
        if instance != self.request.user:
            raise PermissionDenied(_('You can only access your own user data.'))
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Ensure the user can only update their own record.
        """
        instance = self.get_object()
        if instance != self.request.user:
            raise PermissionDenied(_('You can only update your own user data.'))
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Ensure the user can only partially update their own record.
        """
        instance = self.get_object()
        if instance != self.request.user:
            raise PermissionDenied(_('You can only update your own user data.'))
        return super().partial_update(request, *args, **kwargs)


@method_decorator(name='create', decorator=admin_create_collaborator_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_collaborator_swagger)
@method_decorator(name='update', decorator=admin_update_collaborator_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_collaborator_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_collaborator_swagger)
@method_decorator(name='list', decorator=admin_list_collaborator_swagger)
class CollaboratorAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing Collaborator records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = CollaboratorSerializer
    lookup_field = 'id'
    queryset = Collaborator.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['invitation_sender__username', 'invitation_receiver__username', 'status']


@method_decorator(name='create', decorator=user_create_collaborator_swagger)
@method_decorator(name='retrieve', decorator=user_retrieve_collaborator_swagger)
@method_decorator(name='update', decorator=user_update_collaborator_swagger)
@method_decorator(name='partial_update', decorator=user_partial_update_collaborator_swagger)
@method_decorator(name='destroy', decorator=user_destroy_collaborator_swagger)
@method_decorator(name='list', decorator=user_list_collaborator_swagger)
@method_decorator(name='received_invitations', decorator=user_list_received_invitations_swagger)
@method_decorator(name='handle_invitation', decorator=user_handle_invitation_swagger)
class CollaboratorAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Authenticated user API ViewSet for managing own Collaborator records and handling invitations.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CollaboratorSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to collaborations where the user is either sender or receiver.
        """
        return Collaborator.objects.filter(
            Q(invitation_sender=self.request.user) | Q(invitation_receiver=self.request.user)
        )

    def create(self, request, *args, **kwargs):
        """
        Set invitation_sender to authenticated user and prevent modification.
        """
        if 'invitation_sender_id' in request.data and request.data['invitation_sender_id'] != self.request.user.id:
            raise ValidationError(_('Invitation sender must be the authenticated user.'))
        request.data['invitation_sender_id'] = self.request.user.id
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Ensure user can only update their own collaboration records.
        """
        instance = self.get_object()
        if instance.invitation_sender != self.request.user and instance.invitation_receiver != self.request.user:
            raise PermissionDenied(_('You can only update your own collaboration records.'))
        if 'invitation_sender_id' in request.data or 'invitation_receiver_id' in request.data:
            raise ValidationError(_('Sender or receiver cannot be modified.'))
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Ensure user can only partially update their own collaboration records.
        """
        instance = self.get_object()
        if instance.invitation_sender != self.request.user and instance.invitation_receiver != self.request.user:
            raise PermissionDenied(_('You can only update your own collaboration records.'))
        if 'invitation_sender_id' in request.data or 'invitation_receiver_id' in request.data:
            raise ValidationError(_('Sender or receiver cannot be modified.'))
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Ensure user can only delete their own collaboration records.
        """
        instance = self.get_object()
        if instance.invitation_sender != self.request.user and instance.invitation_receiver != self.request.user:
            raise PermissionDenied(_('You can only delete your own collaboration records.'))
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve their own collaboration records.
        """
        instance = self.get_object()
        if instance.invitation_sender != self.request.user and instance.invitation_receiver != self.request.user:
            raise PermissionDenied(_('You can only access your own collaboration records.'))
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def received_invitations(self, request):
        """
        List all pending collaboration invitations received by the authenticated user.
        """
        invitations = Collaborator.objects.filter(
            invitation_receiver=self.request.user,
            status='PENDING'
        )
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def handle_invitation(self, request, id=None):
        """
        Accept or reject a collaboration invitation received by the authenticated user.
        """
        instance = self.get_object()
        if instance.invitation_receiver != self.request.user:
            raise PermissionDenied(_('You can only handle invitations sent to you.'))
        if instance.status != 'PENDING':
            raise ValidationError(_('This invitation has already been handled.'))
        action = request.data.get('action')
        if action not in ['ACCEPT', 'REJECT']:
            raise ValidationError(_('Action must be either ACCEPT or REJECT.'))
        if action == 'ACCEPT':
            success = instance.accept_invitation()
        else:
            success = instance.reject_invitation()
        if not success:
            raise ValidationError(_('Failed to process invitation.'))
        return Response(self.get_serializer(instance).data)