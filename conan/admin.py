from django.contrib import admin
from conan import models

# Register your models here.

@admin.register(models.ItemTypeChoice)
class ItemTypeChoiceAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)
	#list_filter = ('',)

@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'itemtype', 'price', 'stacksize',)
	search_fields = ('name',)
	#list_filter = ('',)

@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
	list_display = ('item',)
	search_fields = ('item',)
	#list_filter = ('',)

@admin.register(models.RecipePart)
class RecipePartAdmin(admin.ModelAdmin):
	list_display = ('recipe', 'item', 'amount')
	search_fields = ('recipe', 'item')
	#list_filter = ('',)