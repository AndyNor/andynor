from django.http import HttpResponseRedirect, HttpResponseForbidden
from datetime import timedelta, datetime
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.contrib.sessions.models import Session
from mysite.site_wide_functions import get_client_ip, get_client_agent
from mysite.models import Counter
from django.middleware import csrf
from django.utils.deprecation import MiddlewareMixin


class CountVisitor(MiddlewareMixin):
	def process_request(self, request):
		if 'visit_counted' not in request.session:
			request.session['visit_counted'] = True

			bad_agents = ('bot', 'spider', 'test', "feed", "crawler", "rss")
			agent = get_client_agent(request)
			if any(bad in agent.lower() for bad in bad_agents):
				return None

			def seen_before(request, ip, agent):
				days = 7
				hits = Counter.objects.values('pk').filter(
					time__gte=timezone.now() - timedelta(days=days),
					ip=ip,
					agent=agent
				)
				#print 'hits %s' % hits.count()
				return True if (hits.count() > 0) else False

			ip = get_client_ip(request)
			if not seen_before(request, ip, agent):
				count = Counter()
				count.ip = ip
				count.agent = agent
				count.save()
				messages.success(request, 'You are %s running %s' % (ip, agent))

		return None


class HTTPSRedirect(MiddlewareMixin):
	def process_request(self, request):
		if request.get_full_path() == "/rss/":
			return None
		if not request.is_secure():
			if getattr(settings, 'SESSION_COOKIE_SECURE', True):
				request_url = request.build_absolute_uri(request.get_full_path())
				secure_url = request_url.replace('http://', 'https://')
				return HttpResponseRedirect(secure_url)


class SessionCleanup(MiddlewareMixin):
	def process_request(self, request):
		Session.objects.filter(expire_date__lte=datetime.now()).delete()


class SecurityHeaders(MiddlewareMixin):
	def process_response(self, request, response):
		#csrf_token = csrf.get_token(request)
		#add -Report-Only for testing
		#CSP is now added using a standardized middleware
		#response['Content-Security-Policy'] = "default-src 'self'; style-src 'unsafe-inline' 'self'; script-src 'nonce-%s' 'self' https://www.youtube.com https://s.ytimg.com https://www.youtube-nocookie.com; frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com" % (csrf_token)
		#response['X-Content-Type-Options'] = "nosniff"
		#response['Cache-Control'] = "max-age=0, no-cache, no-store"
		response['Server'] = "Dude, I don't know"

		#certificate_pin_current = 'pin-sha256="ntaa4dzdzEmjCVMrlFOJTlfUQJKu3LoMqi1qlyCjoek=";'
		#certificate_backup1 = 'pin-sha256="orne4NMB+gRZ5FIMhpzlzLZQ/M6Xk6ml0Fd/c6qp2lQ=";'
		#certificate_backup2 = 'pin-sha256="181NMJKq1c28dYCENy2lsu33dkifRayer4wlWhYAoRg=";'
		#certificate_backup3 = 'pin-sha256="UqUz4zdTsFhzr9rFnCxsyDY0CegeJ80izAudW9HIgNo=";'

		# add -Report-Only for testing
		#response['Public-Key-Pins'] = "%s %s %s %s max-age=5184000;" % (certificate_pin_current, certificate_backup1, certificate_backup2, certificate_backup3)

		noCachePaths = ("/money/", "/profiles/", "/statistics/", "/stocks/")
		if any (path in request.path for path in noCachePaths):
			response['Cache-Control'] = "private, no-store, no-cache"
		return response


