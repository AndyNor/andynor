from django.contrib import admin
from power import models

@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('owner', 'id', 'date', 'kwh_usage', 'kwh_usage_cost', 'kwh_rent_cost', 'fixed_cost')
	list_filter = ('owner',)
	search_fields = ('owner__username', 'owner__email')
	date_hierarchy = 'date'
	ordering = ('-date',)
	list_select_related = ('owner',)

