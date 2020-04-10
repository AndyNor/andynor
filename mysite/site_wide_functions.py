from django.urls import reverse
from django.http import Http404
import json
from django.contrib import messages
from mysite.models import SiteLog

def safe_referrer(request):
	from django.conf import settings
	try:
		referrer = request.META['HTTP_REFERER']
		if settings.SITE_URL not in referrer:
			#messages.info(request, 'Why are you messing with the referrer?')
			referrer = settings.SITE_URL
	except:
		referrer = settings.SITE_URL

	return referrer


def silentremove(request, path):
	import os
	try:
		os.remove(path)
		# messages.success(request, '%s was deleted from disk' % path)
		return True
	except OSError as e:
		if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
			messages.error(request, '%s could not be deleted' % path)
		return False

def add_to_log(request, message, priority=3):  # 1=high, 2=medium, 3=low
	if type(message) in [str,]:
		try:
			person = request.user.get_full_name()
		except:
			person = "Anonymous"
		entry = SiteLog(
			ip=get_client_ip(request),
			user=person,
			message=message,
			priority=priority,
		)
		entry.save()
	else:
		messages.error(request, "Logging: message was not a string, skipping")


def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip


def get_client_agent(request):
	return request.META.get('HTTP_USER_AGENT')


def set_redirect_session(request, page, parameters):
	request.session['redirect_next'] = reverse(page, kwargs=parameters)


def get_previous_page(request, default='root'):
	'''
	Using either GET 'next' or a default to set path for redirection
	'''
	previous_page = request.GET.get('next', None)
	if previous_page is None:
		previous_page = request.session.get('redirect_next', None)
		request.session['redirect_next'] = None
		if previous_page is None:
			previous_page = reverse(default)

	return previous_page


def generate_form(request, model, modelform, pk, initial=False):
	if pk:  # update
		#print pk
		pk = int(pk)
		try:
			instance = model.objects.get(pk=pk)
		except model.DoesNotExist:
			raise Http404
		form = modelform(instance=instance)
		if request.method == 'POST':
			form = modelform(request.POST, request.FILES, instance=instance)
	else:  # new
		if initial:
			form = modelform(initial=initial)
		else:
			form = modelform()
		if request.method == 'POST':
			form = modelform(request.POST, request.FILES)
	return form


def makeJSON(queryset):

	def handleDecimal(object):
		return float(object)

	queryset = list(queryset)
	return json.dumps(queryset, default=handleDecimal)
