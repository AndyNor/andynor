from django.contrib import admin
from stocks.models import Transaction, Ticker, TickerHistory

admin.site.register(Transaction)
admin.site.register(Ticker)
admin.site.register(TickerHistory)

