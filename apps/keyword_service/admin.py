from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Keyword

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'root_keyword', 'keyword_type', 'project', 'search_volume', 'created_at')
    search_fields = ('keyword', 'root_keyword', 'project__name')
    list_filter = ('keyword_type', 'project')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('project',)}),
        (_('Keyword Details'), {'fields': ('root_keyword', 'keyword', 'keyword_type', 'extra_word')}),
        (_('SEO Data'), {'fields': ('search_volume_data', 'geo_search_volume_data', 'search_engine_results', 'search_volume')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')
