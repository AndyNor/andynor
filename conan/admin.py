from django.contrib import admin
from conan import models
from django.shortcuts import redirect
from django.urls import reverse

# Register your models here.

@admin.register(models.ItemTypeChoice)
class ItemTypeChoiceAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	#list_filter = ('',)

	def response_add(self, request, obj, post_url_continue=None):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect(reverse('app_conan'))
		return super().response_add(request, obj, post_url_continue)

	def response_change(self, request, obj):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect(reverse('app_conan'))
		return super().response_change(request, obj)

@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'itemtype', 'stack_price_silver', 'stacksize',)
	search_fields = ('name',)
	#list_filter = ('',)

	def response_add(self, request, obj, post_url_continue=None):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect(reverse('item_details', kwargs={'pk': obj.item.pk}))
		return super().response_add(request, obj, post_url_continue)

	def response_change(self, request, obj):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect(reverse('item_details', kwargs={'pk': obj.item.pk}))
		return super().response_change(request, obj)

@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
	list_display = ('item',)
	search_fields = ('item__name',)
	#list_filter = ('',)

	autocomplete_fields = (
		'item',
		)

	def response_add(self, request, obj, post_url_continue=None):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect(reverse('item_details', kwargs={'pk': obj.item.pk}))
		return super().response_add(request, obj, post_url_continue)

	def response_change(self, request, obj):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect(reverse('item_details', kwargs={'pk': obj.item.pk}))
		return super().response_change(request, obj)

@admin.register(models.RecipePart)
class RecipePartAdmin(admin.ModelAdmin):
	list_display = ('recipe', 'item', 'amount')
	search_fields = ('recipe', 'item')
	#list_filter = ('',)

	autocomplete_fields = (
		'recipe',
		'item',
		)

	def response_add(self, request, obj, post_url_continue=None):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect('/return/')
		return super().response_add(request, obj, post_url_continue)

	def response_change(self, request, obj):
		if not any(header in ('_addanother', '_continue', '_popup') for header in request.POST):
			return redirect('/return/')
		return super().response_change(request, obj)