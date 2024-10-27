from django.urls import include, re_path
from databases import views

urlpatterns =  [
	re_path(r'^edit/$', views.overview_edit, name='databases_options'),

	re_path(r'^edit/(?P<model_name>Category|SubCategory|Series)/$', views.edit, name='databases_new'),
	re_path(r'^edit/(?P<model_name>Category|SubCategory|Series)/(?P<pk>\d{1,12})/$', views.edit, name='databases_edit'),
	re_path(r'^del/(?P<model_name>Category|SubCategory|Series)/(?P<pk>\d{1,12})/$', views.delete, name='databases_del'),

	re_path(r'^edit/(?P<model_name>Data)/(?P<new_type>\w{1,20})/$', views.edit, name='databases_new_data'),
	re_path(r'^edit/(?P<model_name>Data)/(?P<pk>\d{1,12})/(?P<new_type>\w{1,20})/$', views.edit, name='databases_edit_data'),
	re_path(r'^del/(?P<model_name>Data)/(?P<pk>\d{1,12})/$', views.delete, name='databases_del_data'),

	re_path(r'^$', views.overview, name='app_databases'),
	re_path(r'^view/$', views.overview, name='app_databases'),
	re_path(r'^view/(?P<category_name>\w{1,20})/$', views.overview, name='databases_view'),
]
