from django.conf.urls import url
from power import views

urlpatterns = [
	url(r'^$', views.index, name='app_power'),
	url(r'^payment/$', views.payment, name='power_payment'),
	url(r'^payment/(?P<pk>\d{1,12})/$', views.payment, name='power_payment_edit'),
	url(r'^reading/$', views.reading, name='power_reading'),
	url(r'^reset/$', views.reading_reset, name='power_reading_reset'),  # add confirm
	url(r'^reset/(?P<new_state>\d{1,12})/$', views.reading_reset, name='reading_new_state'),  # add confirm
]
