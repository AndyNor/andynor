from django.conf import settings  # Get the media_root variable
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.template import RequestContext  # required for csrf
from django.contrib import messages  # Message system
from django.contrib.auth.decorators import permission_required
import math
import calendar
import os
import re
import hashlib
from mysite.site_wide_functions import get_previous_page, generate_form, get_client_ip, set_redirect_session, silentremove, safe_referrer
from blog import models
from blog.images import img_calc_thumb, img_calc_large, highest_order_nr, image_order_cleanup, image_exists
from blog.images import images_create, images_remove
from django.db.models import Count  # counting frequency of tags for every blog
from django.middleware import csrf

APP_NAME = 'app_blog'

@permission_required('blog.blog.can_add_blog', raise_exception=True)
def list_files(request):
	file_path = settings.FILE_URL
	fo = models.File.objects.all().order_by("-created")
	return render(request, 'blog_file_list.html', {
		'files': fo,
		'file_path': file_path,
	})


def blog_comment(request, blog_pk):
	try:
		blog = models.Blog.objects.get(pk=blog_pk)
		if blog.published and blog.linked:
			if request.method == "POST":
				form = models.CommentForm(request.POST)
				if form.is_valid():
					o = form.save(commit=False)
					o.page = blog
					o.ip = get_client_ip(request)
					try:
						#o.save()
						return HttpResponseRedirect(get_previous_page(request, APP_NAME))
					except:
						return Http404
			else:
				form = models.CommentForm()
		else:
			form = None
			messages.error(request, 'Permission denied')
	except:
		form = None
		messages.error(request, 'Blog ID does not exist')

	set_redirect_session(request, 'blog_show', {'blog_pk': blog_pk})
	return render(request, 'blog_comment.html', {
		'form': form,
		'title': blog.title,
	})


def index(request, blog_pk=False, category_id=1, category_history=False):
	if blog_pk:
		blog_pk = int(blog_pk)
	if category_id:
		category_id = int(category_id)
	if category_history:
		category_history = int(category_history)

	NUM_DISPLAYED_LINKS = 20
	NUM_PAGINATION = 4
	#BLOG_ORDER_BY = ['-sticky', '-updated', '-pk']
	#BLOG_ORDER_BY = ['-sticky', '-origin']
	BLOG_ORDER_BY = ['-origin']
	all_categories = models.Category.objects.filter(visible=True)

	if request.user.is_authenticated:
		blogs_query = models.Blog.objects.all()
		links_query = blogs_query
	else:
		blogs_query = models.Blog.objects.filter(published=True)
		links_query = blogs_query.filter(linked=True)

	blog_history_query = links_query.values('pk', 'title', 'linked', 'published', 'sticky').order_by(*BLOG_ORDER_BY)

	# Get correct blog, category name and links
	if blog_pk:
		try:
			blog_active = blogs_query.get(pk=blog_pk)
		except:
			messages.error(request, 'The blog you tried to get does not exist! (or you don\'t have access to it)')
			return HttpResponseRedirect(reverse('app_blog'))
		category_pk = blog_active.category.pk
		category_name = str(blog_active.category)
		blog_history = blog_history_query.filter(category=blog_active.category.pk)
		if blog_active.category.visible is True:
			request.session['blog_pk_c%s' % category_pk] = blog_pk

	elif category_id:
		try:
			category = models.Category.objects.get(pk=category_id)
			category_name = category.category
			category_pk = category.pk
		except:
			category_name = None
			category_pk = None

		blog_history = blog_history_query.filter(category=category_id)
		blog_pk = request.session.get('blog_pk_c%s' % category_pk, False)
		if blog_pk:
			try:
				blog_active = blogs_query.get(pk=blog_pk)
			except:
				blog_active = blogs_query.filter(
					category=category_id
				).order_by(*BLOG_ORDER_BY)[:1].get()
		else:
			try:
				blog_active = blogs_query.filter(
					category=category_id
				).order_by(*BLOG_ORDER_BY)[:1].get()
			except:
				blog_active = None
		if blog_active != None:
			request.session['blog_pk_c%s' % category_pk] = blog_active.pk

	else:
		blog_active = blogs_query.order_by(*BLOG_ORDER_BY)[:1].get()
		category_name = False
		category_pk = 0
		blog_history = blog_history_query

	if blog_active:
		comments = models.Comment.objects.filter(page=blog_active.pk).order_by('-pk')
	else:
		comments = None

	# Create pagination
	num_blogs = len(blog_history)
	num_pages = int(math.ceil(float(num_blogs) / float(NUM_DISPLAYED_LINKS - 1)))
	# print 'number: %s and pages: %s' % (num_blogs, num_pages)
	pagination = []

	if category_history:
		request.session[('blog_history_c%s' % category_pk)] = category_history
	else:
		category_history = int(request.session.get(('blog_history_c%s' % category_pk), 1))

	pagination_start = (category_history - 1) * (NUM_DISPLAYED_LINKS - 1)
	pagination_end = (category_history * (NUM_DISPLAYED_LINKS - 1)) + 1

	# Goal is to display NUM_PAGINATION items with the selected page in the middle while padding the borders
	# This is not dependent on NUM_PAGINATION...
	if category_history < 3:
		range_start = 1
	elif category_history > num_pages - 2:
		range_start = num_pages - 3
	else:
		range_start = category_history - 2

	# Ending link must never be greater than the total number of pages
	range_end = range_start + NUM_PAGINATION
	if range_end > num_pages:
		range_end = num_pages + 1

	for i in range(range_start, range_end):
		if i > 0:
			if i == category_history:
				html_class = 'active'
			else:
				html_class = ''
			pagination.append({'page': i, 'class': html_class})
	if len(pagination) < 2:
		pagination = None  # don't need to see only one link

	return render(request, 'blog.html', {
		'category_list': all_categories,
		'category_name': category_name,
		'category_pk': category_pk,
		'blog_active': blog_active,
		'comments': comments,
		'blog_history': blog_history[pagination_start:pagination_end],
		'pagination': pagination,
		'page_last': num_pages,
	})


def generate_archive_links(active_year, active_month, years=False):
	distinct_months = models.Blog.objects.filter(published=True)
	if not distinct_months:
		return None

	if years != False:
		from datetime import date
		this_year = date.today().year
		not_after = this_year - years
		start_date = date(not_after, 1, 1)
		distinct_months = distinct_months.filter(origin__gte=start_date)
	distinct_months = distinct_months.dates('origin', 'month', order='DESC')
	distinct_months_length = len(distinct_months)
	distinct_months_pointer = 0

	archive_menu = []

	counter_year_latest = distinct_months[0].year
	counter_year_oldest = distinct_months[distinct_months_length - 1].year
	year_range = range(counter_year_oldest, counter_year_latest + 1)
	month_range = range(1, 13)

	for year in reversed(year_range):
		temp_months = []
		for month in reversed(month_range):
			temp_year = distinct_months[distinct_months_pointer].year
			temp_month = distinct_months[distinct_months_pointer].month
			if temp_year == year and temp_month == month:
				temp_type = 'active' if (year == active_year and month == active_month) else 'enabled'
				if distinct_months_pointer < distinct_months_length - 1:
					distinct_months_pointer += 1
			else:
				temp_type = 'disabled'
			temp_months.append({'month': month, 'name': calendar.month_name[month][:3], 'type': temp_type})
		archive_menu.append({'year': year, 'months': temp_months})

	return archive_menu


def archive(request, year=False, month=False):
	all_categories = models.Category.objects.filter(visible=True)
	year = int(year)
	month = int(month)
	if year and month:
		archive_posts = models.Blog.objects.filter(
				published=True,
				origin__year=year,
				origin__month=month,
		).order_by('-origin', '-pk')
	else:
		archive_posts = None

	blogs_display = []
	if archive_posts:
		for blog in archive_posts:
			comments = models.Comment.objects.filter(page=blog.pk).order_by('-pk')
			blogs_display.append({"content": blog, "comments": comments})
	else:
		blogs_display = None



	return render(request, 'blog_archive.html', {
		'category_list': all_categories,
		'archive_menu': generate_archive_links(year, month),
		'archive_posts': archive_posts,
		'year': year,
		'month': month,
		'blogs_display': blogs_display,
	})


# Login required

@permission_required('blog.blog.can_add_blog', raise_exception=True)
def delete_blog_comment(request, comment_pk):
	csrf_token = csrf.get_token(request)
	request_token = request.GET.get('token')
	if request_token == csrf_token:
		try:
			comment = models.Comment.objects.get(pk=comment_pk)
			comment.delete()
			messages.success(request, 'Commet was deleted!')
		except:
			messages.error(request, 'Comment could not be deleted')
		request.session['redirect_next'] = safe_referrer(request)
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))
	else:
		messages.error(request, u'Token did not match')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def delete_blog(request, blog_pk):

	if request.method == "POST":
		comments = models.Comment.objects.filter(page=blog_pk)
		images = models.Image.objects.filter(blog=blog_pk)
		go_ahead = True
		if comments:
			messages.error(request, 'Delete all comments first!')
			go_ahead = False
		if images:
			messages.error(request, 'Delete all images first!')
			go_ahead = False
		if go_ahead:
			try:
				blog = models.Blog.objects.get(pk=blog_pk)
				title = blog.title
				blog.delete()
				messages.success(request, '%s is gone!' % title)
			except:
				messages.error(request, u'Could not delete post')
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))
	else:
		return render(request, 'blog_delete.html', {
			u'blog_pk': blog_pk,
		})

@permission_required('blog.blog.can_add_blog', raise_exception=True)
def write(request, pk=False):
	blog_form = generate_form(request, models.Blog, models.BlogForm, pk)
	if blog_form.is_valid():
		o = blog_form.save(commit=False)
		o.owner = request.user
		o.save()
		blog_form.save_m2m()
		messages.success(request, u'Blogg added/updated with ID=%s' % o.pk)
		set_redirect_session(request, 'blog_show', {'blog_pk': o.pk})
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	if pk:
		request.session['redirect_next'] = reverse('blog_update', args=[pk])
		try:
			blog = models.Blog.objects.get(pk=pk)
			sub_text = u'editing "%s"' % blog.title
			redirect_url = reverse('blog_show', args=[pk])
		except:
			return Http404
	else:
		sub_text = u'new item'
		redirect_url = None

	return render(request, 'blog_edit.html', {
		u'form': blog_form,
		u'sub_header': sub_text,
		u'redirect': redirect_url,
	})


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def category(request, pk=False):
	category_form = generate_form(request, models.Category, models.CategoryForm, pk, None)
	if category_form.is_valid():
		category_form.save()
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	return render(request, 'blog_edit.html', {
		'form': category_form,
		'entries': models.Category.objects.all(),
	})


def file_unlink(request, blog_id, file_id):
	csrf_token = csrf.get_token(request)
	request_token = request.GET.get('token')
	if request_token == csrf_token:
		obj = models.File.objects.get(pk=file_id)
		rem_path = '%s%s/%s' % (settings.FILE_ROOT, blog_id, obj.filename)
		if silentremove(request, rem_path):
			if obj.delete():
				return True
	else:
		messages.error(request, u'Token did not match')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))

@permission_required('blog.blog.can_add_blog', raise_exception=True)
def file_remove(request, blog_id, file_id):
	file_unlink(request, blog_id, file_id)
	request.session['redirect_next'] = safe_referrer(request)
	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def file_upload(request, blog_id, file_id=False):
	if request.POST:
		form = models.FileForm(request.POST, request.FILES)
		if form.is_valid():
			upload = request.FILES['file']
			filename = re.sub('[^A-Za-z0-9._-]+', '', str(upload).replace(" ", "_"))
			folder = '%s%s/' % (settings.FILE_ROOT, blog_id)
			full_path = '%s%s' % (folder, filename)
			save_to_db = False
			if not os.path.exists(folder):
				os.makedirs(folder)
			if not os.path.exists(full_path):
				try:
					digest = hashlib.sha256()
					with open(full_path, 'wb+') as destination:
						for chunk in upload.chunks():
							digest.update(chunk)
							destination.write(chunk)
					save_to_db = True
				except IOError as e:
					messages.error(request, 'Could not save the file to storage: %s %s') % (e.errno, e)
			else:
				messages.error(request, 'The file already exist')

			if save_to_db:
				if file_id:
					o = models.File.objects.get(pk=file_id)
					file_unlink(request, blog_id, o.pk)
				else:
					o = models.File()
					o.owner = request.user
					o.blog = models.Blog.objects.get(pk=blog_id)

				o.filename = filename
				o.size = upload.size
				o.checksum = digest.hexdigest()
				o.save()


			return HttpResponseRedirect(reverse(file_upload, kwargs={'blog_id': blog_id}))
	else:
		form = models.FileForm

	if not file_id: # not replacing
		blog_files = models.File.objects.filter(blog=blog_id).order_by('-pk')
		set_redirect_session(request, 'blog_show', {'blog_pk': blog_id})
		return render(request, 'file_upload.html', {
			'form': form,
			'files': blog_files,
			'redirect': reverse('blog_show', args=[blog_id]),
		})
	else: # special form for replacement
		try:
			file_obj = models.File.objects.get(pk=file_id)
		except:
			messages.error(request, 'Could not find the file')
		return render(request, 'file_replace.html', {
			'form': form,
			'file': file_obj,
			'redirect': reverse('file_upload', args=[blog_id]),
		})



@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_upload(request, blog_id, image_id=False):
	if request.POST:
		form = models.ImageForm(request.POST, request.FILES)
		if form.is_valid():
			user = request.user
			filename = request.FILES['image']
			if not images_create(request, blog_id, user, filename, image_id):
				messages.error(request, 'Could not save the image to disk. Check "originals" folder and make folder private')
			return HttpResponseRedirect(reverse(img_upload, kwargs={'blog_id': blog_id}))
	else:
		form = models.ImageForm

	if image_id is False:
		blog_images = models.Image.objects.filter(blog=blog_id).order_by('-order')
		set_redirect_session(request, 'blog_show', {'blog_pk': blog_id})
		return render(request, 'image_index.html', {
			'form': form,
			'images': blog_images,
			'redirect': reverse('blog_show', args=[blog_id]),
			#'archive_menu': generate_archive_links(False, False),
		})
	else:
		try:
			blog_image = models.Image.objects.get(pk=image_id)
		except:
			messages.error(request, 'Could not find the image')
		return render(request, 'image_replace.html', {
			'form': form,
			'image': blog_image,
			'redirect': reverse('image_upload', args=[blog_id]),
		})


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_remove(request, image_id):

	try:
		image = models.Image.objects.get(pk=image_id)
	except:
		messages.error(request, 'Image ID could not be found')

	if request.method == "POST":
		images_remove(request, image_id)
		request.session['redirect_next'] = safe_referrer(request)
		return HttpResponseRedirect(reverse('image_upload', args=[image.blog.pk]))
	else:
		return render(request, 'image_delete.html', {
			u'image': image,
		})


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_rethumb(request, image_id):
	image = models.Image.objects.get(pk=image_id)
	img_calc_thumb(request, image, 400, 266)
	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_fullthumb(request, image_id):
	image = models.Image.objects.get(pk=image_id)
	img_calc_thumb(request, image, 800)
	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_relocate(request):
	if 'selected_pictures' in request.POST:
		selected_images = request.POST.getlist('selected_pictures', None)
		request.session['blog_images_selection'] = selected_images
	else:
		selected_images = request.session.get('blog_images_selection', None)

	print(request.POST)

	all_valid = True
	image_objects = []
	if selected_images != None:
		for image_id in selected_images:
			image_id = int(image_id)
			try:
				image = models.Image.objects.get(pk=image_id)
				image_objects.append(image)
			except:
				all_valid = False

		if all_valid is True and len(image_objects) > 0:
			origin_blog = image_objects[0].blog
			if 'blog' in request.POST:
				receiving_blog = request.POST.get('blog', None)
				if receiving_blog != None:
					try:
						receiving_blog_object = models.Blog.objects.get(pk=receiving_blog)
						highest_order = highest_order_nr(receiving_blog_object)
						counter = 1
						for image in image_objects:
							image.blog = receiving_blog_object
							image.order = highest_order + counter
							image.save()
							counter += 1
						image_order_cleanup(origin_blog.pk)
						image_order_cleanup(receiving_blog_object.pk)
						return redirect('image_upload', blog_id=receiving_blog_object.pk)
					except:
						messages.error(request, 'Blog does not exist or unable to move')
			form = models.MoveImagesForm
	else:
		messages.error(request, 'No images selected')
		form = None

	return render(request, 'blog_move.html', {
		'form': form,
		'images': image_objects,
	})


# new 2.jul 2013
@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_comment(request, image_id):
	image = image_exists(request, image_id)
	comment = request.POST.get('comment', None)
	if comment is None:
		return render(request, 'image_comment.html', {
			'image': image,
		})
	else:
		image.description = comment
		try:
			image.save()
			messages.success(request, "Image comment updated!")
			return HttpResponseRedirect(get_previous_page(request, APP_NAME))
		except:
			messages.error(request, "Not able to save comment to image")
			return HttpResponseRedirect(get_previous_page(request, APP_NAME))


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def img_relarge(request, image_id):
	image = image_exists(request, image_id)
	if image:
		if img_calc_large(image, 3840):
			messages.success(request, "Large resize: Image resized!")
		else:
			messages.error(request, "Large resize: original not found")
	else:
		messages.error(request, "Large resize: image not in database")
	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


def tag_view(request, tag=None):

	val_min = 40
	val_max = 230

	if tag:
		blogs = models.Blog.objects.filter(published=True, tags__in=[tag]).order_by('-origin')
	else:
		blogs = None

	#  Following relationships backwards (https://docs.djangoproject.com/en/dev/topics/db/aggregation/)
	freqs = models.Tag.objects.annotate(frequency=Count('blog__tags'))
	if freqs:
		freq_max = freqs.order_by('-frequency')[0].frequency
		for tag in freqs:
			tag.frequency = (float(tag.frequency) / float(freq_max)) * (val_max - val_min) + val_min
	else:
		freqs = None

	return render(request, 'blog_tag_view.html', {
		'tagblogs': blogs,
		'tagfreqs': freqs,
	})


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def tag_edit(request, pk=None):
	blog_form = generate_form(request, models.Tag, models.TagForm, pk)
	if blog_form.is_valid():
		o = blog_form.save(commit=True)
		messages.success(request, u'Tag %s added' % o.tag)
		return HttpResponseRedirect(reverse('blog_tag_add'))
	return render(request, 'blog_tag_form.html', {
		u'form': blog_form,
		u'tags': models.Tag.objects.all(),
	})


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def tag_del(request, pk):
	csrf_token = csrf.get_token(request)
	request_token = request.GET.get('token')
	if request_token == csrf_token:
		try:
			tag = models.Tag.objects.get(pk=pk)
			tag.delete()
			messages.success(request, 'Tag was deleted!')
		except:
			messages.error(request, 'Could not delete the Tag!')
		return HttpResponseRedirect(reverse('blog_tag_add'))
	else:
		messages.error(request, u'Token did not match')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))