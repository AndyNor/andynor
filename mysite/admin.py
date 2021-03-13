from django.contrib import admin
from mysite import models

admin.site.register(models.UserProfile)


@admin.register(models.ApplicationLog)
class BankTransactionAdmin(admin.ModelAdmin):
	list_display = ('opprettet', 'event_type', 'message',)
	search_fields = ('message',)
	list_filter = ('event_type',)


@admin.register(models.SiteLog)
class SiteLogAdmin(admin.ModelAdmin):
	list_display = ('ip', 'priority', 'time', 'user', 'message')
	search_fields = ('message', 'ip',)
	list_filter = ('time', 'priority', 'user',)

@admin.register(models.Counter)
class CounterAdmin(admin.ModelAdmin):
	list_display = ('ip', 'time', 'agent',)
	search_fields = ('ip', 'agent')
	list_filter = ('time', 'agent',)
