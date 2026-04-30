from django.db import models
from django import forms
from django.contrib.auth.models import User
from mysite.models import make_custom_plugins
import datetime
from django.urls import reverse



class Category(models.Model):
	category = models.CharField(max_length=25, unique=True)
	description = models.CharField(max_length=140, blank=True, null=True)
	tabbed = models.BooleanField(default=False)
	grouped = models.BooleanField(default=False)
	visible = models.BooleanField(default=True)

	class Meta:
		verbose_name = "kategori"
		verbose_name_plural = "kategorier"

	def __str__(self):
		return u'%s' % (self.category)

	def save(self, *args, **kwargs):
		self.category = self.category.lower()
		super(Category, self).save(*args, **kwargs)


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = "__all__" 


class Tag(models.Model):
	tag = models.CharField(max_length=25, unique=True)
	description = models.CharField(max_length=140, blank=True, null=True)

	def __str__(self):
		return u'%s' % (self.tag)

	def save(self, *args, **kwargs):
		self.tag = self.tag.lower()
		super(Tag, self).save(*args, **kwargs)

	class Meta:
		verbose_name = "tagg"
		verbose_name_plural = "tagger"
		ordering = ['tag']


class TagForm(forms.ModelForm):
	class Meta:
		model = Tag
		fields = "__all__" 

class Blog(models.Model):
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	category = models.ForeignKey(Category, on_delete=models.PROTECT)
	title = models.CharField(max_length=100, blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	origin = models.DateField(blank=True, null=False, default=datetime.date.today)
	tags = models.ManyToManyField(Tag, blank=True)
	tags.help_text = ''
	content = models.TextField(blank=True, null=True)
	linked = models.BooleanField(default=True)
	published = models.BooleanField(default=False)
	sticky = models.BooleanField(default=False)

	class Meta:
		verbose_name = "blogginnlegg"
		verbose_name_plural = "blogginnlegg"

	def __str__(self):
		return u'%s %s' % (self.pk, self.title)

	def get_absolute_url(self):
		return reverse('blog_show', kwargs={'blog_pk': self.pk})


class BlogForm(forms.ModelForm):
	tags_text = forms.CharField(
		label="Tagger",
		required=False,
		help_text='Skriv tagger separert med mellomrom. Bruk "anførselstegn" for tagger med mellomrom.',
	)

	class Meta:
		model = Blog
		exclude = ('owner', 'created', 'updated', 'tags')
		formfield_callback = make_custom_plugins

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Ensure tags field appears right after `origin` and before `content`.
		if 'tags_text' in self.fields and 'origin' in self.fields:
			tags_field = self.fields.pop('tags_text')
			new_fields = {}
			for name, field in self.fields.items():
				new_fields[name] = field
				if name == 'origin':
					new_fields['tags_text'] = tags_field
			# Fallback: if origin wasn't encountered for some reason, append at end.
			if 'tags_text' not in new_fields:
				new_fields['tags_text'] = tags_field
			self.fields = new_fields

		if self.instance and getattr(self.instance, 'pk', None):
			self.fields['tags_text'].initial = " ".join([t.tag for t in self.instance.tags.order_by('tag')])

	def clean_tags_text(self):
		raw = (self.cleaned_data.get('tags_text') or '').strip()
		if not raw:
			return []

		import shlex

		try:
			parts = shlex.split(raw)
		except ValueError:
			# Fallback: best-effort split on whitespace
			parts = raw.split()

		normalized = []
		seen = set()
		for p in parts:
			tag = str(p).strip().lower()
			if not tag:
				continue
			if tag in seen:
				continue
			seen.add(tag)
			normalized.append(tag)
		return normalized

	def _apply_tags_text(self):
		"""
		Apply `tags_text` to the instance by creating missing Tag rows and
		setting the M2M relation to match the provided tags.
		"""
		tags = self.cleaned_data.get('tags_text')
		if tags is None:
			return

		tag_objs = []
		for tag in tags:
			obj, _created = Tag.objects.get_or_create(tag=tag, defaults={"description": ""})
			tag_objs.append(obj)
		self.instance.tags.set(tag_objs)

	def save(self, commit=True):
		"""
		Django overwrites `save_m2m()` on the *instance* when `save(commit=False)`
		is called. The blog edit view uses that pattern, so we wrap the generated
		`save_m2m()` here to ensure tags are always applied.
		"""
		instance = super().save(commit=commit)

		# If commit=False, Django sets self.save_m2m dynamically; wrap it.
		if not commit:
			original_save_m2m = getattr(self, 'save_m2m', None)

			def _wrapped_save_m2m():
				if callable(original_save_m2m):
					original_save_m2m()
				self._apply_tags_text()

			self.save_m2m = _wrapped_save_m2m
		else:
			# If commit=True, instance is already saved so we can apply immediately.
			self._apply_tags_text()

		return instance


class Comment(models.Model):
	page = models.ForeignKey(Blog, on_delete=models.PROTECT)
	poster = models.CharField(max_length=40, verbose_name='Your name')
	comment = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	ip = models.GenericIPAddressField(null=True)

	class Meta:
		verbose_name = "kommentar"
		verbose_name_plural = "kommentarer"

	def __str__(self):
		return u'%s' % (self.comment[:15])


class Image(models.Model):
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	filename = models.CharField(max_length=50)
	description = models.CharField(max_length=150, blank=True, null=True)
	blog = models.ForeignKey(Blog, on_delete=models.PROTECT)
	original = models.CharField(max_length=50, blank=True, null=True)
	large = models.CharField(max_length=50)
	thumbnail = models.CharField(max_length=50, blank=True, null=True)
	order = models.IntegerField()

	class Meta:
		verbose_name = "bilde"
		verbose_name_plural = "bilder"

	def __str__(self):
		return u'%s - %s' % (self.pk, self.filename)


class ImageForm(forms.Form):
	image = forms.ImageField()


class File(models.Model):
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	blog = models.ForeignKey(Blog, on_delete=models.PROTECT)
	created = models.DateTimeField(auto_now_add=True)
	filename = models.CharField(max_length=255)
	size = models.IntegerField()
	checksum = models.CharField(max_length=256)

	class Meta:
		verbose_name = "fil"
		verbose_name_plural = "filer"

	def __str__(self):
		return u'%s' % (self.filename)

class FileForm(forms.Form):
	file = forms.FileField()

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('poster', 'comment')


class MoveImagesForm(forms.Form):
	blog = forms.ModelChoiceField(queryset=Blog.objects.order_by('-pk'), help_text="Select recieving blog")
