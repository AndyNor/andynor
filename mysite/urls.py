from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from blog.feeds import LatestEntriesFeed
from django.views.generic.base import RedirectView
from mysite import views
from django.urls import path

handler403 = 'mysite.views.my_custom_permission_denied_view'
admin.autodiscover()

# Mysite
urlpatterns = [
	url(r'^$', views.index, name="root"),
	url(r'^login/$', views.user_login, name="user_login"),
	url(r'^logout/$', views.user_logout, name="user_logout"),
	url(r'^password/$', views.password_change, name="password_change"),
	url(r'^contact/$', views.contact_email, name='contact_email'),
	url(r'^search/$', views.search, name='search'),
	url(r'^return/$', views.go_back),
	url(r'^profiles/$', views.profile, name='profile'),
	url(r'^profiles/(?P<profile_id>\d{1,12})/$', views.profile_update, name='profile_update'),
	url(r'^profiles/(?P<profile_id>\d{1,12})/delete/$', views.profile_delete, name='profile_delete'),
	url(r'^statistics/$', views.statistics, name='statistics'),
	url(r'^debug/$', views.debug, name='debug'),
	url(r'^rss/$', LatestEntriesFeed(), name='rss'),
	url(r'^robots\.txt$', RedirectView.as_view( url=settings.STATIC_URL + 'robots.txt')),
]

# Apps
urlpatterns += [
	url(r'^admin/', admin.site.urls, name="admin"),
	path('money/', include('money.urls'), name="money"),
	path('power/', include('power.urls'), name="power"),
	path('blog/', include('blog.urls'), name="blog"),
	path('databases/', include('databases.urls'), name="databases"),
	path('calc/', include('calc.urls'), name="calc"),
	path('stocks/', include('stocks.urls'), name="stocks"),
]


if settings.DEBUG:
	from django.views.static import serve
	_media_url = settings.MEDIA_URL
	if _media_url.startswith('/'):
		_media_url = _media_url[1:]
		urlpatterns += [
				url(r'^%s(?P<path>.*)$' % _media_url,
				serve,
				{'document_root': settings.MEDIA_ROOT})]
	del(_media_url, serve)
