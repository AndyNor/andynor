from django.contrib import admin

from blog import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('category', 'id', 'visible', 'tabbed', 'grouped')
	list_filter = ('visible', 'tabbed', 'grouped')
	search_fields = ('category', 'description')


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('tag', 'id', 'description')
	search_fields = ('tag', 'description')


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
	list_display = (
		'title',
		'id',
		'category',
		'origin',
		'published',
		'linked',
		'owner',
		'updated',
	)
	list_filter = ('published', 'linked', 'category')
	search_fields = ('title', 'content', 'tags__tag')
	date_hierarchy = 'origin'
	list_select_related = ('category', 'owner')
	ordering = ('-updated',)


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('page', 'id', 'poster', 'comment_preview', 'created', 'ip')
	list_select_related = ('page',)
	search_fields = ('comment', 'poster', 'page__title')
	list_filter = ('created',)

	@admin.display(description='Comment')
	def comment_preview(self, obj):
		text = (obj.comment or '')[:80]
		return text + ('…' if len(obj.comment or '') > 80 else '')


@admin.register(models.Image)
class ImageAdmin(admin.ModelAdmin):
	list_display = ('filename', 'id', 'blog', 'order', 'description_preview')
	list_select_related = ('blog', 'owner')
	search_fields = ('filename', 'description', 'blog__title')
	list_filter = ('blog',)

	@admin.display(description='Description')
	def description_preview(self, obj):
		text = (obj.description or '')[:60]
		return text + ('…' if len(obj.description or '') > 60 else '')


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
	list_display = ('filename', 'id', 'blog', 'size', 'created', 'owner')
	list_select_related = ('blog', 'owner')
	search_fields = ('filename', 'checksum', 'blog__title')
	list_filter = ('created',)
