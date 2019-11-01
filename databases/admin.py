from django.contrib import admin
from databases.models import Data, Series, SubCategory, Category

class DataAdmin(admin.ModelAdmin):
	list_display = ('name', 'category', 'subcategory', 'series', 'flagged', 'star', 'series_nr', 'duration', 'writer')
	list_filter = ('category', 'flagged', 'star')
	search_fields = ('name',)
	#autocomplete_fields = ('',)
admin.site.register(Data, DataAdmin)


class SeriesAdmin(admin.ModelAdmin):
	list_display = ('name',)
	#list_filter = ('')
	search_fields = ('name',)
	#autocomplete_fields = ('',)
admin.site.register(Series, SeriesAdmin)


class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	#list_filter = ('')
	search_fields = ('name',)
	#autocomplete_fields = ('',)
admin.site.register(Category, CategoryAdmin)


class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	#list_filter = ('')
	search_fields = ('name',)
	#autocomplete_fields = ('',)
admin.site.register(SubCategory, SubCategoryAdmin)
