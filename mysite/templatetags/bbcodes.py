#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
from django import template
from django.contrib import messages  # Message system
from blog.models import Image
from django.conf import settings  # Get the media_root variable
from functools import partial
register = template.Library()
from databases.models import Data
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.http import urlencode
from django.middleware import csrf


# Inspired by https://code.djangoproject.com/wiki/CookBookTemplateFilterBBCode

def link_db(matchobj):
	link_ref = matchobj.group(1)
	try:
		link = Data.objects.get(pk=link_ref)
		if link.category.name == 'links':
			return '<a href="%s" rel="tooltip" title="%s" target="_blank">%s</a>' % (link.url, link.text, link.name)
		else:
			return '%s != a link' % link_ref
	except:
		return 'URL id=%s not found' % link_ref


def list_unordered(matchobj):
	html = []
	html.append('<ul>')
	parts = matchobj.group(1).rsplit('* ')
	first = True
	for part in parts:
		if first:
			first = False  # avoid empty line
			continue
		html.append('<li>%s</li>' % part)
	html.append('</ul>')
	return ''.join(html)


def list_ordered(matchobj):
	inverse = ' reversed' if matchobj.group(1) != '' else ''
	html = []
	html.append('<ol%s>' % inverse)
	parts = matchobj.group(2).rsplit('# ')
	first = True
	for part in parts:
		if first:
			first = False  # avoid empty line
			continue
		html.append('<li>%s</li>' % part)
	html.append('</ol>')
	return ''.join(html)


def gallery(request, blog_id, matchobj):
	start = int(matchobj.group(1))
	end = int(matchobj.group(2))
	html = []
	if start <= end and start > 0:
		demanded_images = end - start
		printed_images = 0
		stop = int(end) + 1
		html.append('<div class="row-fluid"><ul class="thumbnails">')
		images = Image.objects.filter(blog=blog_id).order_by('order')[start - 1:stop - 1]
		for image in images:
			html.append('<li class="span3 displayInlineBlock">')
			path = '%s%s' % (settings.MEDIA_ROOT, image.thumbnail)
			title = image.description if image.description != None else ''
			if request.user.is_authenticated:
				edit_button = ('<a href="%s?next=%s"><i class="icon-pencil"></i></a>') % (
						reverse('image_add_comment', args=(image.pk,)),
						request.get_full_path()
				)
			else:
				edit_button = ''
			if os.path.isfile(path):
				html.append('<a href="%s%s"><img width="100%%" class="thumbnail" src="\static\img\loader.gif" data-src="%s%s" alt="%s"></a><small>%s %s</small>' % (
						settings.MEDIA_URL,
						image.large,
						settings.MEDIA_URL,
						image.thumbnail,
						title,
						edit_button,
						title,

						)
				)
			else:
				html.append('<img class="thumbnail" src="%s%s" alt="Image missing">' % (
					settings.STATIC_URL,
					'img/image_missing.png'
					)
				)
			html.append('</li>')
			if(printed_images % 4 == 3):
				html.append('</ul></div><div class="row-fluid"><ul class="thumbnails">')
			printed_images += 1

		if demanded_images >= printed_images:
			remaining = demanded_images - printed_images
			for i in range(remaining + 1):
				if(printed_images % 4 == 0):
					html.append('</ul></div><div class="row-fluid"><ul class="thumbnails">')
				printed_images += 1
				html.append('<li class="span3"><img class="thumbnail" src="%s%s" alt="Image missing"></a>' % (
					settings.STATIC_URL,
					'img/image_upload.png'
					)
				)
		html.append('</ul></div>')

	else:
		return 'Gallery: Check the range'

	return ''.join(html)

def video_link(matchobj):
	from blog import models
	from django.conf import settings
	file_id = int(matchobj.group(1))

	description = "%s" % matchobj.group(2)
	if description == "None":
		description = ""

	try:
		file_obj = models.File.objects.get(pk=file_id)
	except:
		return '<p>File with ID %s does not exist' % (file_id)
	filename = file_obj.filename.split(".")
	url = "%s%s/%s" % (settings.FILE_URL, file_obj.blog.pk, file_obj.filename)

	return '<video width="100%%" controls><source src="%s" type="video/mp4">HTML5 video fungerer ikke i din nettleser</video><small>%s</small><br class="clearBoth">' % (
			url,
			description,
			)	


def file_link(matchobj):
	from blog import models
	from django.conf import settings
	file_id = int(matchobj.group(1))

	description = "%s" % matchobj.group(2)
	if description == "None":
		description = ""

	#http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
	def sizeof_fmt(num):
		for x in ['bytes','KiB','MiB','GiB','TiB']:
			if num < 1024.0:
				return "%3.1f %s" % (num, x)
			num /= 1024.0

	try:
		file_obj = models.File.objects.get(pk=file_id)
	except:
		return '<p>File with ID %s does not exist' % (file_id)
	filename = file_obj.filename.split(".")
	name = '.'.join(filename[:-1])
	ext = filename[-1]
	supported = ("zip", "pdf", "exe", "bin", "wav", "torrent", "py", "mp4", "avi", "xlsx", "doc", "txt", "csv")
	icon = None
	for item in supported:
		#print ("%s %s") % (item, ext.lower())
		if item == ext.lower():
			icon = item
	if icon is None:
		icon = "unknown"
	url = "%s%s/%s" % (settings.FILE_URL, file_obj.blog.pk, file_obj.filename)

	return '<div><a href="%s"><img class="floatLeft filePreviewMargin" src="/static/img/files/%s.png">%s</a>%s<br><u>size</u> %s<br>sha256: %s...%s</div><br class="clearBoth">' % (
			url,
			icon,
			name,
			description,
			sizeof_fmt(file_obj.size),
			file_obj.checksum[:10],
			file_obj.checksum[-10:],
			)

def image(request, blog_id, matchobj):
	image_id = int(matchobj.group(1))
	image_class = matchobj.group(2)
	if image_class == '':
		image_class = 'norm'
	image_border = matchobj.group(3)
	if image_border == "no":
		add_border = ""
	else:
		add_border = "class=\"image_border\" "
	try:
		image = Image.objects.get(pk=image_id)
		html = []
		if request.user.is_authenticated:
			edit_button = ('<a href="%s?next=%s"><i class="icon-pencil"></i></a>') % (
					reverse('image_add_comment', args=(image.pk,)),
					request.get_full_path()
			)
		else:
			edit_button = ''
		title = image.description if image.description != None else ''
		html.append('<div class="%s"><img %ssrc="\static\img\loader.gif" data-src="%s%s" width="100%%" alt="%s"></a><br><small>%s %s</small></div>' % (
				image_class,
				add_border,
				settings.MEDIA_URL,
				image.large,
				title,
				edit_button,
				title,

			)
		)
		return ''.join(html)
	except:
		return '<img class="" src="%s%s" alt="Image missing"></a>' % (
					settings.STATIC_URL,
					'img/image_upload.png'
					)


def thumb(request, blog_id, matchobj):
	image_id = int(matchobj.group(1))
	image_class = matchobj.group(2)
	if image_class == '':
		image_class = 'norm'
	image_border = matchobj.group(3)
	if image_border == "no":
		add_border = ""
	else:
		add_border = "class=\"image_border\" "
	try:
		image = Image.objects.get(pk=image_id)
		html = []
		if request.user.is_authenticated:
			edit_button = ('<a href="%s?next=%s"><i class="icon-pencil"></i></a>') % (
				reverse('image_add_comment', args=(image.pk,)),
				request.get_full_path()
			)
		else:
			edit_button = ''
		title = image.description if image.description != None else ''
		html.append('<div class="%s"><a href="%s%s"><img %s src="\static\img\loader.gif" data-src="%s%s" alt="%s"></a><br><small>%s %s</small></div>' % (
				image_class,
				settings.MEDIA_URL,
				image.large,
				add_border,
				settings.MEDIA_URL,
				image.thumbnail,
				title,
				edit_button,
				title,
				)
		)
		return ''.join(html)
	except:
		return '<img class="" src="%s%s" alt="Image missing"></a>' % (
					settings.STATIC_URL,
					'img/image_upload.png'
				)



def bbcode_render(context, text, blog_id):
	#csrf_token = csrf.get_token(context['request'])
	if not blog_id:
		messages.warning(context['request'], 'Cannot replace images without a blog ID in the bbcode tag')

	bbdata = [
			# Containers
			(r'\[code\](.+?)\[!code\]', r'<pre class="prettyprint code">\1</pre>'),
			(r'\[well\](.+?)\[!well\]', r'<div class="well">\1</div>'),
			(r'\[lead\](.+?)\[!lead\]', r'<p class="lead">\1</p>'),
			(r'\[quote\]([^@]+?)\[!quote\]', r'<blockquote>\1</blockquote>'),
			(r'\[quote\](.+?)@(.+?)\[!quote\]', r'<blockquote>\1<small>\2</small></blockquote>'),

			# Semi-containers
			(r'\[ul\](.+?)\[!ul\]', partial(list_unordered)),
			(r'\[ol(| inv)\](.+?)\[!ol\]', partial(list_ordered)),
			(r'\[hr\]', r'<hr>'),
			(r'\[clear\]', r'<div class="clearBoth"></div>'),

			# youtube
			(r'\[tube\](.+?) (.+?) (.+?)\[!tube\]', r'<iframe width="100%" height="380" src="https://www.youtube.com/embed/\1?rel=0&start=\2&end=\3" frameborder="0" allow="encrypted-media" allowfullscreen></iframe>'),


			# Links
			(r'\[link=([^,]*),([^,]*),(self|blank)\]', r'<a class="link_\3" href="\1" target="_\3">\2</a>'),
			(r'\[url=(\d{1,10})\]', partial(link_db)),
			(r'\[url\](.+?) (.+?)\[!url\]', r'<a href="\1">\2</a>'),

			# Images
			(r'\[gallery=(?P<start>\d{1,3})-(?P<end>\d{1,3})\]', partial(gallery, context['request'], blog_id)),
			(r'\[img=(\d{1,10})[\s,]?(|norm|right|left)[\s,]?(|yes|no)\]', partial(image, context['request'], blog_id)),
			(r'\[thumb=(\d{1,10})[\s,]?(|norm|right|left)[\s,]?(|yes|no)\]', partial(thumb, context['request'], blog_id)),
			(r'\[video=(?P<id>\d{1,10})(\s(?P<desc>[^\]]+))?\]', partial(video_link)),


			# Text formating
			(r'\[highlight\](.+?)\[!highlight\]', r'<span class="text_highlight">\1</span>'),
			(r'\[title=(.+?)\]', r'<h4>\1</h4>'),
			(r'\[tykk=(.+?)\]', r'<b>\1</b>'),
			(r'\[skjev=(.+?)\]', r'<i>\1</i>'),
			(r'\[under=(.+?)\]', r'<u>\1</u>'),
			(r'\[stryk=(.+?)\]', r'<span class="textLineThrough">\1</span>'),

			# Icons
			(r'\[mindmap=([^\]]*)\]', r'<div><a class="link_ext" target="_blank" href="\1"><img class="mindmapPreviewMargin src="/static/img/mindmap.png">\1</a></div><br class="clearBoth">'),
			(r'\[file=([^,\]]*),([^,\]]*),([^,\]]*)\]', r'<div><a href="/static/files/\1.\2"><img class="floatLeft filePreviewMargin" src="/static/img/files/\2.png">\1</a><br>\3</div><br class="clearBoth">'),
			(r'\[file=(?P<id>\d{1,10})(\s(?P<desc>[^\]]+))?\]', partial(file_link)),

	]

	for bbset in bbdata:
		p = re.compile(bbset[0], re.DOTALL)
		text = p.sub(bbset[1], text)

	return '<div class="textJustify">%s</div>' % text


@register.simple_tag(takes_context=True)
def bbcode(context, **kwargs):
	text = kwargs.get('text', None)
	if text is None:
		raise template.TemplateSyntaxError("Dictionary element 'text' is missing.")
	else:
		blog_id = kwargs.get('blog_id', False)
		return mark_safe(bbcode_render(context, text, blog_id))
