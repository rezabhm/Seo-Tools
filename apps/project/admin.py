from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Project, Process

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'service_url', 'created_at')
    search_fields = ('name', 'owner__username', 'service_url')
    list_filter = ('owner',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('name', 'owner')}),
        (_('Project Details'), {'fields': ('description', 'service_url', 'banner', 'collaborators')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25
    filter_horizontal = ('collaborators',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner').prefetch_related('collaborators')

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('project', 'status', 'extraction_level', 'total_count', 'completed_count', 'created_at')
    search_fields = ('project__name',)
    list_filter = ('status', 'project')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('project',)}),
        (_('Process Details'), {'fields': ('status', 'extraction_level', 'total_count', 'completed_count')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')
