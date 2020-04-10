from django import forms
from django.db import models
from mysite.models import make_custom_plugins
from django.conf import settings


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return u'%s' % (self.name)

	def save(self, *args, **kwargs):
		self.name = self.name.lower()
		super(Category, self).save(*args, **kwargs)

	class Meta:
		verbose_name_plural = "Kategorier"
		ordering = ['name']


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = "__all__"


class SubCategory(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return u'%s' % (self.name)

	def save(self, *args, **kwargs):
		self.name = self.name.lower()
		super(SubCategory, self).save(*args, **kwargs)

	class Meta:
		ordering = ['name']
		verbose_name_plural = "Subkategorier"


class SubCategoryForm(forms.ModelForm):
	class Meta:
		model = SubCategory
		fields = "__all__"


class Series(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return u'%s' % (self.name)

	def save(self, *args, **kwargs):
		self.name = self.name.lower()
		super(Series, self).save(*args, **kwargs)

	class Meta:
		ordering = ['name']
		verbose_name_plural = "Serier"


class SeriesForm(forms.ModelForm):
	class Meta:
		model = Series
		fields = "__all__"


class Data(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(Category, on_delete=models.PROTECT)
	name = models.CharField(max_length=100)
	subcategory = models.ForeignKey(SubCategory, blank=True, null=True, on_delete=models.SET_NULL)
	url = models.URLField(blank=True, null=True, help_text=u'Optional')
	flagged = models.BooleanField(default=False, help_text=u'Audible: Read, Software: Cost, TVseries: Active')
	star = models.BooleanField(default=False, help_text=u'If it stands out')
	writer = models.CharField(max_length=100, blank=True, null=True, help_text=u'Optional')
	series = models.ForeignKey(Series, blank=True, null=True, help_text=u'Optional', on_delete=models.SET_NULL)
	series_nr = models.IntegerField("Part #", blank=True, null=True, help_text=u'Optional')
	produced = models.DateField("Release", blank=True, null=True, help_text=u'Release date')
	text = models.TextField("Description", blank=True, null=True, help_text=u'TV-siers: description')
	duration = models.IntegerField("Duration", blank=True, null=True, help_text=u'[minutes]')
	image = models.ImageField(upload_to="database_images",
		height_field=None,
		width_field=None,
		max_length=100,
		blank=True,
		null=True,
		)

	def __str__(self):
		return u'%s' % (self.name)

	class Meta:
		verbose_name_plural = "Registrerte ting"


class DataForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Data
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super(DataForm, self).__init__(*args, **kwargs)
		self.fields['text'].widget.attrs['class'] = "small"
