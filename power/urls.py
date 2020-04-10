from django.conf.urls import url
from power import views

urlpatterns = [
	url(r'^$', views.index, name='app_power'),
	url(r'^payment/$', views.payment, name='power_payment'),
	url(r'^payment/(?P<pk>\d{1,12})/$', views.payment, name='power_payment_edit'),
]
