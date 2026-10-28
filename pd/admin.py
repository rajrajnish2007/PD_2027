
from django.contrib import admin
from .models import IndependentAdjudicator


@admin.register(IndependentAdjudicator)
class IndependentAdjudicatorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'institution_name',
        'contact_number',
        'email',
        'created_at',
    )

    search_fields = (
        'name',
        'institution_name',
        'contact_number',
        'email',
    )

    list_filter = ('created_at',)
