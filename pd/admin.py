from django.contrib import admin

# Register your models here.
#RAJNISH START
from .models import InstitutionalTeam


@admin.register(InstitutionalTeam)
class InstitutionalTeamAdmin(admin.ModelAdmin):
    list_display = (
        'institution_name',
        'team_rep_names',
        'team_slots',
        'adjudicator_slots',
        'contact_number',
        'email',
        'created_at',
    )
    search_fields = (
        'institution_name',
        'team_rep_names',
        'contact_number',
        'email',
    )
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

# Ashmitha START
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
#Ashmitha END


# RAJNISH START
from .models import CrossTeam


@admin.register(CrossTeam)
class CrossTeamAdmin(admin.ModelAdmin):
    list_display = (
        'team_name',
        'team_leader_name',
        'adjudicator_slots',
        'contact_number',
        'email',
        'created_at',
    )
    search_fields = (
        'team_name',
        'team_leader_name',
        'contact_number',
        'email',
    )
    list_filter = ('created_at',)
# RAJNISH END
