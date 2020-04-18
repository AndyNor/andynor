from django.contrib import admin
from mysite import models

admin.site.register(models.SiteLog)
admin.site.register(models.Counter)
admin.site.register(models.UserProfile)


@admin.register(models.ApplicationLog)
class BankTransactionAdmin(admin.ModelAdmin):
	list_display = ('opprettet', 'event_type', 'message',)
	search_fields = ('message',)
	list_filter = ('event_type',)
