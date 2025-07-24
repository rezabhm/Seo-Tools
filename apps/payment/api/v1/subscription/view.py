from django.db.models import ProtectedError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, filters, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from apps.payment.models.subscription import SubscriptionPlan, PlanFeature, UserSubscription
from apps.payment.serializers.subscription import SubscriptionPlanSerializer, PlanFeatureSerializer, UserSubscriptionSerializer
from apps.payment.api.v1.subscription.swagger_decorator import (
    admin_create_subscription_plan_swagger,
    admin_retrieve_subscription_plan_swagger,
    admin_update_subscription_plan_swagger,
    admin_partial_update_subscription_plan_swagger,
    admin_destroy_subscription_plan_swagger,
    admin_list_subscription_plan_swagger,
    admin_create_plan_feature_swagger,
    admin_retrieve_plan_feature_swagger,
    admin_update_plan_feature_swagger,
    admin_partial_update_plan_feature_swagger,
    admin_destroy_plan_feature_swagger,
    admin_list_plan_feature_swagger,
    admin_create_user_subscription_swagger,
    admin_retrieve_user_subscription_swagger,
    admin_update_user_subscription_swagger,
    admin_partial_update_user_subscription_swagger,
    admin_destroy_user_subscription_swagger,
    admin_list_user_subscription_swagger,
    user_list_subscription_plan_swagger,
    user_retrieve_user_subscription_swagger,
    user_list_user_subscription_swagger,
)
import logging

# Configure logging
logger = logging.getLogger(__name__)

@method_decorator(name='create', decorator=admin_create_subscription_plan_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_subscription_plan_swagger)
@method_decorator(name='update', decorator=admin_update_subscription_plan_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_subscription_plan_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_subscription_plan_swagger)
@method_decorator(name='list', decorator=admin_list_subscription_plan_swagger)
class SubscriptionPlanAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing SubscriptionPlan records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = SubscriptionPlanSerializer
    lookup_field = 'id'
    queryset = SubscriptionPlan.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['price', 'keyword_limit']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "This subscription plan is in use and cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST  # or 409 Conflict
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

@method_decorator(name='create', decorator=admin_create_plan_feature_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_plan_feature_swagger)
@method_decorator(name='update', decorator=admin_update_plan_feature_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_plan_feature_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_plan_feature_swagger)
@method_decorator(name='list', decorator=admin_list_plan_feature_swagger)
class PlanFeatureAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing PlanFeature records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = PlanFeatureSerializer
    lookup_field = 'id'
    queryset = PlanFeature.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['description', 'subscription_plan__price']

@method_decorator(name='create', decorator=admin_create_user_subscription_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_user_subscription_swagger)
@method_decorator(name='update', decorator=admin_update_user_subscription_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_user_subscription_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_user_subscription_swagger)
@method_decorator(name='list', decorator=admin_list_user_subscription_swagger)
class UserSubscriptionAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing UserSubscription records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = UserSubscriptionSerializer
    lookup_field = 'id'
    queryset = UserSubscription.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'subscription_plan__price']

@method_decorator(name='list', decorator=user_list_subscription_plan_swagger)
class SubscriptionPlanReadOnlyAPIView(
    GenericViewSet,
    mixins.ListModelMixin,
):
    """
    Read-only API ViewSet for authenticated users to view SubscriptionPlan records with their features.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer
    queryset = SubscriptionPlan.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['price', 'keyword_limit']

@method_decorator(name='retrieve', decorator=user_retrieve_user_subscription_swagger)
@method_decorator(name='list', decorator=user_list_user_subscription_swagger)
class UserSubscriptionReadOnlyAPIView(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    Read-only API ViewSet for authenticated users to view their own UserSubscription records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSubscriptionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Restrict queryset to subscriptions belonging to the authenticated user.
        """
        return UserSubscription.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """
        Ensure user can only retrieve their own subscriptions.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied(_('You can only access your own subscriptions.'))
        return super().retrieve(request, *args, **kwargs)