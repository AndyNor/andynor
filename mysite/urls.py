from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from blog.feeds import LatestEntriesFeed
from django.views.generic.base import RedirectView
from mysite import views
from django.urls import path

handler403 = 'mysite.views.my_custom_permission_denied_view'
admin.autodiscover()

# Mysite
urlpatterns = [
	re_path(r'^$', views.index, name="root"),
	re_path(r'^forside/$', views.index, name="forside"),
	re_path(r'^articles/more/$', views.home_articles_more, name="home_articles_more"),
	re_path(r'^articles/newer/$', views.home_articles_newer, name="home_articles_newer"),
	re_path(r'^articles/year/$', views.home_articles_year, name="home_articles_year"),
	re_path(r'^articles/month/$', views.home_articles_month, name="home_articles_month"),
	re_path(r'^articles/index/$', views.home_articles_index, name="home_articles_index"),
	re_path(r'^articles/html/$', views.home_articles_html, name="home_articles_html"),
	re_path(r'^login/$', views.user_login, name="user_login"),
	re_path(r'^logout/$', views.user_logout, name="user_logout"),
	re_path(r'^password/$', views.password_change, name="password_change"),
	re_path(r'^contact/$', views.contact_email, name='contact_email'),
	re_path(r'^search/$', views.search, name='search'),
	re_path(r'^return/$', views.go_back),
	re_path(r'^profiles/$', views.profile, name='profile'),
	path('counter/<int:year>/<int:month>/', views.counter, name='counter'),
	re_path(r'^profiles/update/$', views.profile_update, name='profile_update'),
	re_path(r'^rss/$', LatestEntriesFeed(), name='rss'),
	re_path(r'^robots\.txt$', RedirectView.as_view( url=settings.STATIC_URL + 'robots.txt')),
]

# Apps
urlpatterns += [
	re_path(r'^admin/', admin.site.urls, name="admin"),
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
				re_path(r'^%s(?P<path>.*)$' % _media_url,
				serve,
				{'document_root': settings.MEDIA_ROOT})]
	del(_media_url, serve)
