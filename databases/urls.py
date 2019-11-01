from django.conf.urls import url
from databases import views

urlpatterns =  [
	url(r'^edit/$', views.overview_edit, name='databases_options'),

	url(r'^edit/(?P<model_name>Category|SubCategory|Series)/$', views.edit, name='databases_new'),
	url(r'^edit/(?P<model_name>Category|SubCategory|Series)/(?P<pk>\d{1,12})/$', views.edit, name='databases_edit'),
	url(r'^del/(?P<model_name>Category|SubCategory|Series)/(?P<pk>\d{1,12})/$', views.delete, name='databases_del'),

	url(r'^edit/(?P<model_name>Data)/(?P<new_type>\w{1,20})/$', views.edit, name='databases_new_data'),
	url(r'^edit/(?P<model_name>Data)/(?P<pk>\d{1,12})/(?P<new_type>\w{1,20})/$', views.edit, name='databases_edit_data'),
	url(r'^del/(?P<model_name>Data)/(?P<pk>\d{1,12})/$', views.delete, name='databases_del_data'),

	url(r'^$', views.overview, name='app_databases'),
	url(r'^view/$', views.overview, name='app_databases'),
	url(r'^view/(?P<category_name>\w{1,20})/$', views.overview, name='databases_view'),
]
