from django.contrib import admin
from stocks import models

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('pk', 'ticker', 'date', 'amount', 'total_price', 'brokerage')
	list_filter = ('ticker',)


admin.site.register(models.Ticker)
admin.site.register(models.TickerHistory)

