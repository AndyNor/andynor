from django.db import models, transaction
from django import forms
from django.contrib.auth.models import User
from mysite.models import make_custom_plugins
import datetime
from django.urls import reverse



class Category(models.Model):
	category = models.CharField('Kategori', max_length=25, unique=True)
	description = models.CharField('Beskrivelse', max_length=140, blank=True, null=True)
	visible = models.BooleanField('Synlig', default=True)
	default_choice = models.BooleanField(
		'Standardvalg',
		default=False,
		help_text=(
			'Kun én kategori kan være standard om gangen. '
			'Når du krysser av her, fjernes standardvalg fra alle andre kategorier.'
		),
	)

	class Meta:
		verbose_name = "kategori"
		verbose_name_plural = "kategorier"

	def __str__(self):
		return u'%s' % (self.category)

	def save(self, *args, **kwargs):
		self.category = self.category.lower()
		if self.default_choice:
			with transaction.atomic():
				qs = Category.objects.filter(default_choice=True)
				if self.pk is not None:
					qs = qs.exclude(pk=self.pk)
				qs.update(default_choice=False)
				super(Category, self).save(*args, **kwargs)
		else:
			super(Category, self).save(*args, **kwargs)


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = "__all__"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for name in ('visible', 'default_choice'):
			if name not in self.fields:
				continue
			widget = self.fields[name].widget
			if isinstance(widget, forms.CheckboxInput):
				extra = 'blog-write-option-input'
				cls = (widget.attrs.get('class', '') + ' ' + extra).strip()
				widget.attrs['class'] = cls


class Tag(models.Model):
	tag = models.CharField('Tagg', max_length=25, unique=True)
	description = models.CharField('Beskrivelse', max_length=140, blank=True, null=True)

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
	owner = models.ForeignKey(
		User,
		on_delete=models.PROTECT,
		verbose_name='Eier',
	)
	category = models.ForeignKey(
		Category,
		on_delete=models.PROTECT,
		verbose_name='Kategori',
	)
	title = models.CharField('Tittel', max_length=100, blank=True, null=True)
	created = models.DateTimeField('Opprettet', auto_now_add=True)
	updated = models.DateTimeField('Oppdatert', auto_now=True)
	origin = models.DateField(
		'Dato',
		blank=True,
		null=False,
		default=datetime.date.today,
		help_text='Dato innlegget vises under (sortering og visning).',
	)
	tags = models.ManyToManyField(
		Tag,
		blank=True,
		verbose_name='Tagger',
		help_text='',
	)
	content = models.TextField('Innhold', blank=True, null=True)
	linked = models.BooleanField(
		default=True,
		verbose_name='Lenket',
		help_text=(
			'Vis innlegget i bloggmenyer, på forsiden og i kategorilister for besøkende. '
			'Uten avkryssing er det skjult der, men et publisert innlegg kan fortsatt åpnes med direktelenke. '
			'Kommentarer er bare tilgjengelige når innlegget både er publisert og lenket.'
		),
	)
	published = models.BooleanField(
		default=False,
		verbose_name='Publisert',
		help_text=(
			'Gjør innlegget synlig for besøkende som ikke er innlogget. '
			'Uten avkryssing er det et utkast som kun er synlig for deg (og andre med skrivetilgang) når dere er innlogget.'
		),
	)

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

		for name in ('linked', 'published'):
			if name not in self.fields:
				continue
			widget = self.fields[name].widget
			if isinstance(widget, forms.CheckboxInput):
				extra = 'blog-write-option-input'
				cls = (widget.attrs.get('class', '') + ' ' + extra).strip()
				widget.attrs['class'] = cls

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
	page = models.ForeignKey(
		Blog,
		on_delete=models.PROTECT,
		verbose_name='Innlegg',
	)
	poster = models.CharField('Navn', max_length=40)
	comment = models.TextField('Kommentar')
	created = models.DateTimeField('Opprettet', auto_now_add=True)
	ip = models.GenericIPAddressField('IP-adresse', null=True)

	class Meta:
		verbose_name = "kommentar"
		verbose_name_plural = "kommentarer"

	def __str__(self):
		return u'%s' % (self.comment[:15])


class Image(models.Model):
	owner = models.ForeignKey(
		User,
		on_delete=models.PROTECT,
		verbose_name='Eier',
	)
	filename = models.CharField('Filnavn', max_length=50)
	description = models.CharField('Beskrivelse', max_length=150, blank=True, null=True)
	blog = models.ForeignKey(
		Blog,
		on_delete=models.PROTECT,
		verbose_name='Blogginnlegg',
	)
	original = models.CharField('Original', max_length=50, blank=True, null=True)
	large = models.CharField('Stor versjon', max_length=50)
	thumbnail = models.CharField('Miniatyrbilde', max_length=50, blank=True, null=True)
	order = models.IntegerField('Rekkefølge')

	class Meta:
		verbose_name = "bilde"
		verbose_name_plural = "bilder"

	def __str__(self):
		return u'%s - %s' % (self.pk, self.filename)


class ImageForm(forms.Form):
	image = forms.ImageField(label='Bilde')


class File(models.Model):
	owner = models.ForeignKey(
		User,
		on_delete=models.PROTECT,
		verbose_name='Eier',
	)
	blog = models.ForeignKey(
		Blog,
		on_delete=models.PROTECT,
		verbose_name='Blogginnlegg',
	)
	created = models.DateTimeField('Opprettet', auto_now_add=True)
	filename = models.CharField('Filnavn', max_length=255)
	size = models.IntegerField('Størrelse (bytes)')
	checksum = models.CharField('Sjekksum', max_length=256)

	class Meta:
		verbose_name = "fil"
		verbose_name_plural = "filer"

	def __str__(self):
		return u'%s' % (self.filename)

class FileForm(forms.Form):
	file = forms.FileField(label='Fil')

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('poster', 'comment')


class MoveImagesForm(forms.Form):
	blog = forms.ModelChoiceField(
		queryset=Blog.objects.order_by('-pk'),
		label='Mål-blogg',
		help_text='Velg blogginnlegget bildene skal flyttes til.',
	)
