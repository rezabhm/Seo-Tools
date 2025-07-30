from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PaymentTransaction, SubscriptionPlan, PlanFeature, UserSubscription

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('paypal_transaction_id', 'user', 'subscription_plan', 'amount', 'status', 'created_at')
    search_fields = ('paypal_transaction_id', 'user__username', 'subscription_plan__price')
    list_filter = ('status', 'subscription_plan')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'paypal_transaction_id')
    fieldsets = (
        (None, {'fields': ('user', 'subscription_plan')}),
        (_('Transaction Details'), {'fields': ('paypal_transaction_id', 'amount', 'status', 'paypal_response', 'redirect_url')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'subscription_plan')

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('price', 'keyword_limit', 'is_labeling_enabled', 'is_chatgpt_enabled', 'is_free_plan', 'created_at')
    search_fields = ('price',)
    list_filter = ('is_labeling_enabled', 'is_chatgpt_enabled', 'is_free_plan')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('price', 'keyword_limit')}),
        (_('Features'), {'fields': ('is_labeling_enabled', 'is_chatgpt_enabled', 'is_free_plan')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('description', 'subscription_plan', 'created_at')
    search_fields = ('description', 'subscription_plan__price')
    list_filter = ('subscription_plan',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('subscription_plan',)}),
        (_('Feature Details'), {'fields': ('description',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscription_plan')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_plan', 'expire_time', 'keywords_extracted', 'keywords_extracted_percent', 'created_at')
    search_fields = ('user__username', 'subscription_plan__price')
    list_filter = ('subscription_plan',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user', 'subscription_plan')}),
        (_('Subscription Details'), {'fields': ('expire_time', 'keywords_extracted', 'keywords_extracted_percent')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'subscription_plan')
