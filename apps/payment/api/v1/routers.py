from rest_framework.routers import DefaultRouter
from apps.payment.api.v1.payment.view import (
    PaymentTransactionAdminAPIView,
    PaymentTransactionAPIView,
    PaymentTransactionReadOnlyAPIView,
)
from apps.payment.api.v1.subscription.view import (
    SubscriptionPlanAdminAPIView,
    PlanFeatureAdminAPIView,
    UserSubscriptionAdminAPIView,
    SubscriptionPlanReadOnlyAPIView,
    UserSubscriptionReadOnlyAPIView,
)

router = DefaultRouter()

router.register(r'admin/subscription-plans', SubscriptionPlanAdminAPIView, basename='admin-subscription-plan')
router.register(r'admin/plan-features', PlanFeatureAdminAPIView, basename='admin-plan-feature')
router.register(r'admin/user-subscriptions', UserSubscriptionAdminAPIView, basename='admin-user-subscription')
router.register(r'subscription-plans', SubscriptionPlanReadOnlyAPIView, basename='subscription-plan')
router.register(r'user-subscriptions', UserSubscriptionReadOnlyAPIView, basename='user-subscription')

router.register(r'admin/transactions', PaymentTransactionAdminAPIView, basename='admin-payment-transaction')
router.register(r'transactions', PaymentTransactionAPIView, basename='payment-transaction')
router.register(r'transactions/read-only', PaymentTransactionReadOnlyAPIView, basename='payment-transaction-read-only')

urlpatterns = router.urls
