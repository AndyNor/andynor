from django.urls import reverse
from django.http import Http404
import json
from django.contrib import messages
from mysite.models import SiteLog
import errno

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
	Using either GET 'next' or session 'redirect_next' or a default to set path for redirection.
	Same-site absolute URLs (e.g. from HTTP_REFERER) are normalized to a relative path.
	'''
	from urllib.parse import urlparse, parse_qs, urlencode
	from django.utils.http import url_has_allowed_host_and_scheme

	candidate = request.GET.get('next')
	if candidate is not None:
		request.session.pop('redirect_next', None)
	else:
		candidate = request.session.pop('redirect_next', None)
	if not candidate:
		return reverse(default)

	candidate = str(candidate).strip()
	if not candidate:
		return reverse(default)

	parsed = urlparse(candidate)
	if parsed.scheme or parsed.netloc:
		if not url_has_allowed_host_and_scheme(
			url=candidate,
			allowed_hosts={request.get_host()},
			require_https=False,
		):
			return reverse(default)
		path = parsed.path or '/'
		redirect_to = '%s?%s' % (path, parsed.query) if parsed.query else path
	else:
		if not candidate.startswith('/') or candidate.startswith('//'):
			return reverse(default)
		redirect_to = candidate

	if not url_has_allowed_host_and_scheme(
		url=redirect_to,
		allowed_hosts={request.get_host()},
		require_https=False,
	):
		return reverse(default)

	login_path = reverse('user_login').rstrip('/') or '/login'
	rd_parsed = urlparse(redirect_to)
	rd_path = (rd_parsed.path or '/').rstrip('/')
	if rd_path == login_path.rstrip('/'):
		return reverse(default)

	# Guard against redirecting to JSON-only "articles" endpoints when coming
	# from edit forms (e.g. image comment edit). Those endpoints are intended
	# for XHR/infinite-scroll and will render as raw JSON in the browser.
	try:
		blocked_paths = {
			'/articles/more/',
			'/articles/newer/',
			'/articles/year/',
			'/articles/month/',
			'/articles/index/',
			'/articles/html/',
		}
		if rd_parsed.path in blocked_paths:
			qs = parse_qs(rd_parsed.query or '')
			params = {}
			if 'cats' in qs and qs['cats']:
				params['cats'] = qs['cats'][-1]
			elif 'cat' in qs and qs['cat']:
				params['cats'] = ','.join(qs['cat'])
			target = reverse(default)
			if params:
				target = '%s?%s' % (target, urlencode(params))
			redirect_to = target
	except Exception:
		pass

	return redirect_to


def url_with_fragment(url, fragment):
	"""Append or replace the URL fragment (hash). ``fragment`` without leading #."""
	if not fragment:
		return url
	frag = fragment.lstrip('#')
	base = url.split('#', 1)[0]
	return '%s#%s' % (base, frag)


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


def csrf_query_token_valid(request, query_token):
	"""Validate ``?token=`` using the CSRF secret (not string-equal to ``get_token()``)."""
	from django.middleware.csrf import (
		CsrfViewMiddleware,
		InvalidTokenFormat,
		_check_token_format,
		_does_token_match,
	)

	if not query_token:
		return False
	try:
		_check_token_format(query_token)
	except InvalidTokenFormat:
		return False

	middleware = CsrfViewMiddleware(lambda req: None)
	try:
		secret = middleware._get_secret(request)
	except InvalidTokenFormat:
		return False
	if secret is None:
		return False
	return _does_token_match(query_token, secret)
