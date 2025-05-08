from django.contrib import admin
from .models import Annotation

@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'permalink', 'version')
    list_filter = ('user', 'version')
    search_fields = ('id', 'user', 'permalink')
    readonly_fields = ('id', 'version')
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'permalink', 'annotation', 'version')
        }),
    )