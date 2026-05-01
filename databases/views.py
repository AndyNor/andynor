from django.shortcuts import render
from django.http import HttpResponseRedirect  # redirect after successfull POST
from django.template import RequestContext  # required for csrf
from mysite.site_wide_functions import get_previous_page, generate_form
from django.contrib.auth.decorators import permission_required
from databases import models
from django.urls import reverse
from django.contrib import messages  # Message system
from django.middleware import csrf
from django.db.models import Count, Q

APP_NAME = 'app_databases'

SUBCATEGORY_FILTER_CATEGORIES = frozenset({'games', 'movies', 'tvseries'})

STARRED_RECENT_CATEGORIES = frozenset({'audible', 'books', 'games', 'movies', 'tvseries'})

DATABASE_CATEGORY_LABELS_NB = {
	'audible': 'Lydbøker',
	'books': 'Bøker',
	'games': 'Spill',
	'movies': 'Filmer',
	'tvseries': 'TV-serier',
	'programs': 'Programmer',
	'links': 'Lenker',
	'spotify': 'Spotify',
	'quotes': 'Sitater',
}

# Font Awesome 6 class strings (solid unless noted) for category nav buttons
DATABASE_CATEGORY_ICONS = {
	'audible': 'fa-solid fa-headphones',
	'books': 'fa-solid fa-book',
	'games': 'fa-solid fa-gamepad',
	'movies': 'fa-solid fa-film',
	'tvseries': 'fa-solid fa-tv',
	'programs': 'fa-solid fa-display',
	'links': 'fa-solid fa-link',
	'spotify': 'fa-brands fa-spotify',
	'quotes': 'fa-solid fa-quote-left',
}


def _category_label_nb(name):
	if not name:
		return 'Databaser'
	return DATABASE_CATEGORY_LABELS_NB.get(name, name.replace('_', ' ').capitalize())


# Generic object to store data
class Object(object):
	pass


def overview(request, category_name=None):
	category_list = models.Category.objects.all()

	def sort(category_name):
		check = {
				'audible': ['writer', 'series', 'series_nr'],
				'movies': ['-produced', '-pk'],
				'tvseries': ['-pk'],
				'programs': ['subcategory', '-star', '-pk'],
				'links': ['subcategory', '-pk'],
				'games': ['-produced', '-pk'],
				'books': ['writer', 'series_id', 'series_nr'],
		}
		sort = check.get(category_name, ['-pk'])
		return sort

	if not category_name:
		return HttpResponseRedirect(reverse('databases_view', args=[u'audible']))

	request.session['redirect_next'] = reverse('databases_view', args=[category_name])
	category_pk = None
	item_list = None
	try:
		category_pk = models.Category.objects.get(name=category_name).pk
		item_list = models.Data.objects.filter(
			category=category_pk
		).order_by(*sort(category_name))
	except models.Category.DoesNotExist:
		pass

	starred_recent_list = None
	if category_name in STARRED_RECENT_CATEGORIES and category_pk is not None:
		starred_recent_list = list(
			models.Data.objects.filter(
				category_id=category_pk,
				star=True,
			).order_by('-created')[:10]
		)

	audible_filter = None
	subcategory_filter = None
	if category_name == 'audible' and category_pk is not None:
		base = models.Data.objects.filter(category=category_pk)
		writers_for_filter = list(
			base.exclude(writer__isnull=True)
			.exclude(writer='')
			.values('writer')
			.annotate(audible_book_count=Count('pk'))
			.order_by('-audible_book_count', 'writer')
		)
		series_ids = base.exclude(series__isnull=True).values_list(
			'series_id', flat=True
		).distinct()
		series_for_filter = (
			models.Series.objects.filter(pk__in=series_ids)
			.annotate(
				audible_book_count=Count(
					'data',
					filter=Q(data__category_id=category_pk),
				)
			)
			.order_by('-audible_book_count', 'name')
		)
		sub_ids = base.exclude(subcategory__isnull=True).values_list(
			'subcategory_id', flat=True
		).distinct()
		subcategories_for_filter = models.SubCategory.objects.filter(pk__in=sub_ids).order_by('name')

		writer_param = (request.GET.get('writer') or '').strip()
		series_param = (request.GET.get('serie') or '').strip()
		kategori_param = (request.GET.get('kategori') or '').strip()
		lest_param = (request.GET.get('lest') or '').strip().lower()
		if lest_param not in ('ja', 'nei'):
			lest_param = ''

		if writer_param:
			item_list = item_list.filter(writer=writer_param)
		if series_param:
			try:
				item_list = item_list.filter(series_id=int(series_param))
			except (TypeError, ValueError):
				pass
		if kategori_param:
			try:
				item_list = item_list.filter(subcategory_id=int(kategori_param))
			except (TypeError, ValueError):
				pass
		if lest_param == 'ja':
			item_list = item_list.filter(flagged=True)
		elif lest_param == 'nei':
			item_list = item_list.filter(flagged=False)

		audible_filter = {
			'writers': writers_for_filter,
			'series_list': series_for_filter,
			'subcategories': subcategories_for_filter,
			'selected_writer': writer_param,
			'selected_serie': series_param,
			'selected_kategori': kategori_param,
			'selected_lest': lest_param,
		}

	elif category_name in SUBCATEGORY_FILTER_CATEGORIES and category_pk is not None:
		base = models.Data.objects.filter(category=category_pk)
		sub_ids = base.exclude(subcategory__isnull=True).values_list(
			'subcategory_id', flat=True
		).distinct()
		subcategories_for_filter = models.SubCategory.objects.filter(pk__in=sub_ids).order_by(
			'name'
		)
		kategori_param = (request.GET.get('kategori') or '').strip()
		if kategori_param:
			try:
				item_list = item_list.filter(subcategory_id=int(kategori_param))
			except (TypeError, ValueError):
				pass
		subcategory_filter = {
			'subcategories': subcategories_for_filter,
			'selected_kategori': kategori_param,
		}

	page_head_title = '%s — AndyNor.net' % (_category_label_nb(category_name),)

	return render(request, ['databases_view_%s.html' % category_name, 'databases.html'], {
		'category_list': category_list,
		'category_name': category_name,
		'item_list': item_list,
		'audible_filter': audible_filter,
		'subcategory_filter': subcategory_filter,
		'starred_recent_list': starred_recent_list,
		'page_head_title': page_head_title,
		'database_category_labels': DATABASE_CATEGORY_LABELS_NB,
		'database_category_icons': DATABASE_CATEGORY_ICONS,
	})


def overview_edit(request):
	return render(request, 'databases_edit_overview.html', {
	})


@permission_required('databases.data.can_add_data', raise_exception=True)
def edit(request, model_name, pk=None, new_type=None):
	model = getattr(models, model_name)
	form_name = '%sForm' % model_name
	model_form = getattr(models, form_name)

	if model_name == 'Data' and new_type != None:
		#print("model name er Data")
		try:
			new_type_pk = models.Category.objects.get(name=new_type).pk
		except:
			new_type_pk = None
		form = generate_form(request, model, model_form, pk, {'category': new_type_pk})
	else:
		form = generate_form(request, model, model_form, pk, None)

	if form.is_valid():
		form.save()
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	if model_name == 'Data':
		return render(request, 'databases_edit_data.html', {
			'form': form,
			'type': model_name,
		})
	else:
		return render(request, 'databases_edit.html', {
			'form': form,
			'type': model_name,
			'entries': model.objects.values('pk', 'name'),
		})


@permission_required('databases.data.can_add_data', raise_exception=True)
def delete(request, model_name, pk=None, new_type=None):
	csrf_token = csrf.get_token(request)
	request_token = request.GET.get('token')
	if request_token == csrf_token:
		model = getattr(models, model_name)
		o = model.objects.get(pk=pk)
		from django.db.models.deletion import ProtectedError
		try:
			o.delete()
		except ProtectedError:
			messages.error(request, 'Det finnes fortsatt oppføringer som bruker dette feltet.')

		if model_name == 'Data':
			return HttpResponseRedirect(get_previous_page(request, APP_NAME))
		else:
			return HttpResponseRedirect(reverse('databases_new', args=[model_name]))
	else:
		messages.error(request, 'Token stemte ikke.')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


