from django.shortcuts import render
from django.http import HttpResponseRedirect  # redirect after successfull POST
from django.template import RequestContext  # required for csrf
from mysite.site_wide_functions import get_previous_page, generate_form
from django.contrib.auth.decorators import permission_required
from databases import models
from django.urls import reverse
from django.contrib import messages  # Message system
from django.middleware import csrf

APP_NAME = 'app_databases'


# Generic object to store data
class Object(object):
	pass


def overview(request, category_name=None):
	category_list = models.Category.objects.all()

	def sort(category_name):
		check = {
				'audible': ['subcategory', 'writer', 'series', 'series_nr'],
				'movies': ['-produced', '-pk'],
				'tvseries': ['-flagged', '-pk'],
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
	try:
		category_pk = models.Category.objects.get(name=category_name).pk

		item_list = models.Data.objects.filter(
				category=category_pk
		).order_by(*sort(category_name))
	except:
		item_list = None

	return render(request, ['databases_view_%s.html' % category_name, 'databases.html'], {
		'category_list': category_list,
		'category_name': category_name,
		'item_list': item_list,
	})


def overview_edit(request):
	return render(request, 'databases_edit_overview.html', {
	})


@permission_required('databases.data.can_add_data', raise_exception=True)
def edit(request, model_name, pk=None, new_type=None):
	model = getattr(models, model_name)
	form_name = '%sForm' % model_name
	model_form = getattr(models, form_name)

	if model_name == 'Data' and new_type is not None:
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
			messages.error(request, "There are still database entries relying on this field!")

		if model_name == 'Data':
			return HttpResponseRedirect(get_previous_page(request, APP_NAME))
		else:
			return HttpResponseRedirect(reverse('databases_new', args=[model_name]))
	else:
		messages.error(request, u'Token did not match')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))


