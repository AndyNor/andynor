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

	def __str__(self):
		return u'%s' % (self.category)

	def save(self, *args, **kwargs):
		self.category = self.category.lower()
		super(Category, self).save(*args, **kwargs)


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = "__all__" 


class Group(models.Model):
	name = models.CharField(max_length=25, unique=True)

	def __str__(self):
		return u'%s' % (self.name)

	def save(self, *args, **kwargs):
		self.name = self.name.lower()
		super(Group, self).save(*args, **kwargs)


class GroupForm(forms.ModelForm):
	class Meta:
		model = Group
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
	group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.PROTECT)
	linked = models.BooleanField(default=True)
	published = models.BooleanField(default=False)
	sticky = models.BooleanField(default=False)

	def __str__(self):
		return u'%s %s' % (self.pk, self.title)

	def get_absolute_url(self):
		return reverse('blog_show', kwargs={'blog_pk': self.pk})


class BlogForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Blog
		exclude = ('owner', 'created', 'updated')


class Comment(models.Model):
	page = models.ForeignKey(Blog, on_delete=models.PROTECT)
	poster = models.CharField(max_length=40, verbose_name='Your name')
	comment = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	ip = models.GenericIPAddressField(null=True)

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
