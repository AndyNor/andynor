from django.urls import include, re_path
from power import views

urlpatterns = [
	re_path(r'^$', views.index, name='app_power'),
	re_path(r'^payment/$', views.payment, name='power_payment'),
	re_path(r'^payment/(?P<pk>\d{1,12})/$', views.payment, name='power_payment_edit'),
]
