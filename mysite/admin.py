from django.contrib import admin
from mysite import models

@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'id', 'name', 'surname', 'BANK_SECRET_EXPIRE')
	search_fields = ('name', 'surname', 'user__username', 'user__email')
	list_filter = ('BANK_SECRET_EXPIRE',)
	autocomplete_fields = ('user',)
	list_select_related = ('user',)


@admin.register(models.ApplicationLog)
class ApplicationLogAdmin(admin.ModelAdmin):
	list_display = ('opprettet', 'id', 'event_type', 'message',)
	search_fields = ('message',)
	list_filter = ('event_type',)
	date_hierarchy = 'opprettet'
	ordering = ('-opprettet',)


@admin.register(models.SiteLog)
class SiteLogAdmin(admin.ModelAdmin):
	list_display = ('ip', 'id', 'priority', 'time', 'user', 'message')
	search_fields = ('message', 'ip', 'user')
	list_filter = ('priority', 'user', 'time')
	date_hierarchy = 'time'
	ordering = ('-time',)

@admin.register(models.Counter)
class CounterAdmin(admin.ModelAdmin):
	list_display = ('ip', 'id', 'time', 'agent',)
	search_fields = ('ip', 'agent')
	list_filter = ('time', 'agent',)
	date_hierarchy = 'time'
	ordering = ('-time',)
