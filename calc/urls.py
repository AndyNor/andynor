from django.urls import include, re_path
from calc import views

urlpatterns = [
	re_path(r'^$', views.index, name='app_calc'),
	re_path(r'^tax/$', views.tax, name='calc_tax'),
	re_path(r'^tax/(?P<year>\d{4})/$', views.tax, name='calc_tax_year'),
	re_path(r'^loan/$', views.loan, name='calc_loan'),
]
