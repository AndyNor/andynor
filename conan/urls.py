from django.urls import include, re_path, path
from conan import views

urlpatterns = [
	re_path(r'^$', views.index, name='app_conan'),
	re_path(r'details/(?P<pk>\d{1,20})/$', views.item_details, name='item_details'),
	re_path(r'orders/$', views.orders, name='orders'),
	re_path(r'details/(?P<pk>\d{1,20})/?format=json$', views.item_details_api, name='item_details_api_json'),
	re_path(r'apiview/order/$', views.all_orders, name='all_orders'),
	re_path(r'apiview/order/(?P<pk>\d{1,20})/$', views.order_details_api, name='order_details_api'),
	re_path(r'apiview/item/$', views.all_items, name='all_items'),
	re_path(r'apiview/item/(?P<pk>\d{1,20})/$', views.item_details_api, name='item_details_api'),
	path('api/', include('conan.apiurls')),
]
