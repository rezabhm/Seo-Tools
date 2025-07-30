from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Collaborator

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email', 'profile_image')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_per_page = 25

@admin.register(Collaborator)
class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('invitation_sender', 'invitation_receiver', 'status', 'created_at')
    search_fields = ('invitation_sender__username', 'invitation_receiver__username')
    list_filter = ('status',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('invitation_sender', 'invitation_receiver')}),
        (_('Invitation Details'), {'fields': ('status',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('invitation_sender', 'invitation_receiver')
