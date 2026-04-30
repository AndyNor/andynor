from django.contrib import admin
from stocks import models

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('ticker', 'id', 'date', 'amount', 'total_price', 'brokerage')
	list_filter = ('ticker',)
	search_fields = ('ticker__company_name', 'ticker__ticker_name')
	date_hierarchy = 'date'
	list_select_related = ('ticker',)


@admin.register(models.Ticker)
class TickerAdmin(admin.ModelAdmin):
	list_display = ('company_name', 'id', 'ticker_name')
	search_fields = ('company_name', 'ticker_name')
	ordering = ('company_name',)


@admin.register(models.TickerHistory)
class TickerHistoryAdmin(admin.ModelAdmin):
	list_display = ('ticker', 'id', 'date', 'price')
	list_filter = ('ticker',)
	search_fields = ('ticker__company_name', 'ticker__ticker_name')
	date_hierarchy = 'date'
	list_select_related = ('ticker',)
	ordering = ('-date',)

