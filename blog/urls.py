from django.conf.urls import url
from blog import views

urlpatterns = [
	url(r'^$', views.index, name='app_blog'),
	url(r'^(?P<blog_pk>\d{1,12})/$', views.index, name='blog_show'),
	url(r'^c(?P<category_id>\d{1,12})/$', views.index, name='blog_category'),
	url(r'^c(?P<category_id>\d{1,12})/h(?P<category_history>\d{1,12})/$', views.index, name='category_history'),
	url(r'^category/edit/$', views.category, name='blog_category_new'),
	url(r'^category/edit/(?P<pk>\d{1,12})/$', views.category, name='blog_category_edit'),
	url(r'^write/$', views.write, name='blog_new'),
	url(r'^write/(?P<pk>\d{1,12})/$', views.write, name='blog_update'),
	url(r'^delete/(?P<blog_pk>\d{1,12})/', views.delete_blog, name='blog_delete'),
	url(r'^files/$', views.list_files, name='list_files'),

	url(r'^image/upload/(?P<blog_id>\d{1,12})/$', views.img_upload, name='image_upload'),
	url(r'^image/upload/(?P<blog_id>\d{1,12})/(?P<image_id>\d{1,12})/$', views.img_upload, name='image_upload_replace'),
	url(r'^image/remove/(?P<image_id>\d{1,12})/$', views.img_remove, name='image_remove'),
	url(r'^image/thumbsmall/(?P<image_id>\d{1,12})/$', views.img_rethumb, name='image_recalculate_thumb'),
	url(r'^image/thumbfull/(?P<image_id>\d{1,12})/$', views.img_fullthumb, name='image_fullsize_thumb'),
	url(r'^image/fullrecalc/(?P<image_id>\d{1,12})/$', views.img_relarge, name='image_regen_large'),
	url(r'^image/move/$', views.img_relocate, name='change_blog_ref'),
	url(r'^image/comment/(?P<image_id>\d{1,12})$', views.img_comment, name='image_add_comment'),

	url(r'^file/upload/(?P<blog_id>\d{1,12})/$', views.file_upload, name='file_upload'),
	url(r'^file/upload/(?P<blog_id>\d{1,12})/(?P<file_id>\d{1,12})/$', views.file_upload, name='file_replace'),
	url(r'^file/remove/(?P<blog_id>\d{1,12})/(?P<file_id>\d{1,12})/$', views.file_remove, name='file_remove'),

	url(r'^comment/(?P<blog_pk>\d{1,12})/$', views.blog_comment, name='blog_comment'),
	url(r'^comment/delete/(?P<comment_pk>\d{1,12})/$', views.delete_blog_comment, name='blog_comment_delete'),

	url(r'^tag/view/$', views.tag_view, name='blog_tag'),
	url(r'^tag/view/(?P<tag>\d{1,12})/$', views.tag_view, name='blog_tag_view'),
	url(r'^tag/edit/$', views.tag_edit, name='blog_tag_add'),
	url(r'^tag/edit/(?P<pk>\d{1,12})/$', views.tag_edit, name='blog_tag_edit'),
	url(r'^tag/del/(?P<pk>\d{1,12})/$', views.tag_del, name='blog_tag_del'),

	url(r'^archive/$', views.archive, name='blog_archive'),
	url(r'^archive/(?P<year>\d{4})/$', views.archive, name='blog_archive_year'),
	url(r'^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.archive, name='blog_archive_month'),


]
