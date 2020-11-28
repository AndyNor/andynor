from django.conf.urls import url
from conan import views

urlpatterns = [
	url(r'^$', views.index, name='app_conan'),
	url(r'details/(?P<pk>\d{1,20})/$', views.item_details, name='item_details'),
]
