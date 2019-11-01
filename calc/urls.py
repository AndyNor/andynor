from django.conf.urls import url
from calc import views

urlpatterns = [
	url(r'^$', views.index, name='app_calc'),
	url(r'^tax/$', views.tax, name='calc_tax'),
	url(r'^tax/(?P<year>\d{4})/$', views.tax, name='calc_tax_year'),
	url(r'^loan/$', views.loan, name='calc_loan'),
]
