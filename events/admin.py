"""Admin configuration for events app."""

from django.contrib import admin
from .models import (
    Event, PricingPhase, VIPTable, BudgetLine,
    InstagramPost, TicketSale, SimulationScenario
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'venue', 'capacity', 'venue_approval_received']
    list_filter = ['venue_approval_received', 'date']
    search_fields = ['name', 'venue']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'venue', 'date', 'capacity', 'opening_time', 'closing_time')
        }),
        ('Contrat venue', {
            'fields': (
                'venue_total_ht', 'venue_total_ttc', 'venue_deposit', 'venue_balance',
                'venue_caution', 'tpe_commission', 'sacem_rate',
                'venue_approval_required', 'venue_approval_received'
            )
        }),
        ('Staff & VIP', {
            'fields': ('staff_count', 'vip_invited_count', 'vip_cost_per_person')
        }),
    )


@admin.register(PricingPhase)
class PricingPhaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'start_date', 'end_date', 'price_solo', 'total_places', 'sold_places']
    list_filter = ['event', 'phase_code']
    ordering = ['event', 'start_date']


@admin.register(VIPTable)
class VIPTableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'event', 'formula', 'is_booked', 'double_order', 'net_revenue']
    list_filter = ['event', 'is_booked', 'formula']
    ordering = ['event', 'table_number']


@admin.register(BudgetLine)
class BudgetLineAdmin(admin.ModelAdmin):
    list_display = ['name', 'event', 'amount', 'timing', 'section', 'is_optional']
    list_filter = ['event', 'section', 'timing']
    ordering = ['event', 'section', 'order']


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'scheduled_date', 'phase', 'post_type', 'assigned_to', 'people_names', 'status']
    list_filter = ['event', 'status', 'post_type', 'phase']
    ordering = ['scheduled_date']
    search_fields = ['title', 'content']


@admin.register(TicketSale)
class TicketSaleAdmin(admin.ModelAdmin):
    list_display = ['event', 'sale_date', 'ticket_type', 'gender', 'quantity', 'amount']
    list_filter = ['event', 'gender', 'ticket_type']
    date_hierarchy = 'sale_date'


@admin.register(SimulationScenario)
class SimulationScenarioAdmin(admin.ModelAdmin):
    list_display = ['event', 'scenario_type', 'total_pax', 'net_result', 'margin_percent']
    list_filter = ['event', 'scenario_type']
