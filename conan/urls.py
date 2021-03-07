from django.conf.urls import url
from django.urls import include, path
from conan import views

urlpatterns = [
	url(r'^$', views.index, name='app_conan'),
	url(r'details/(?P<pk>\d{1,20})/$', views.item_details, name='item_details'),
	url(r'orders/$', views.orders, name='orders'),
	url(r'details/(?P<pk>\d{1,20})/?format=json$', views.item_details_api, name='item_details_api_json'),
	url(r'apiview/item/(?P<pk>\d{1,20})/$', views.item_details_api, name='item_details_api'),
	url(r'apiview/order/(?P<pk>\d{1,20})/$', views.order_details_api, name='order_details_api'),
	url(r'apiview/all_items/$', views.all_items, name='all_items'),
	path('api/', include('conan.apiurls')),
]
