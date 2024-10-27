from django.urls import include, re_path
from blog import views

urlpatterns = [
	re_path(r'^$', views.index, name='app_blog'),
	re_path(r'^(?P<blog_pk>\d{1,12})/$', views.index, name='blog_show'),
	re_path(r'^c(?P<category_id>\d{1,12})/$', views.index, name='blog_category'),
	re_path(r'^c(?P<category_id>\d{1,12})/h(?P<category_history>\d{1,12})/$', views.index, name='category_history'),
	re_path(r'^category/edit/$', views.category, name='blog_category_new'),
	re_path(r'^category/edit/(?P<pk>\d{1,12})/$', views.category, name='blog_category_edit'),
	re_path(r'^write/$', views.write, name='blog_new'),
	re_path(r'^write/(?P<pk>\d{1,12})/$', views.write, name='blog_update'),
	re_path(r'^delete/(?P<blog_pk>\d{1,12})/', views.delete_blog, name='blog_delete'),
	re_path(r'^files/$', views.list_files, name='list_files'),

	re_path(r'^image/upload/(?P<blog_id>\d{1,12})/$', views.img_upload, name='image_upload'),
	re_path(r'^image/upload/(?P<blog_id>\d{1,12})/(?P<image_id>\d{1,12})/$', views.img_upload, name='image_upload_replace'),
	re_path(r'^image/remove/(?P<image_id>\d{1,12})/$', views.img_remove, name='image_remove'),
	re_path(r'^image/thumbsmall/(?P<image_id>\d{1,12})/$', views.img_rethumb, name='image_recalculate_thumb'),
	re_path(r'^image/thumbfull/(?P<image_id>\d{1,12})/$', views.img_fullthumb, name='image_fullsize_thumb'),
	re_path(r'^image/fullrecalc/(?P<image_id>\d{1,12})/$', views.img_relarge, name='image_regen_large'),
	re_path(r'^image/move/$', views.img_relocate, name='change_blog_ref'),
	re_path(r'^image/comment/(?P<image_id>\d{1,12})$', views.img_comment, name='image_add_comment'),

	re_path(r'^file/upload/(?P<blog_id>\d{1,12})/$', views.file_upload, name='file_upload'),
	re_path(r'^file/upload/(?P<blog_id>\d{1,12})/(?P<file_id>\d{1,12})/$', views.file_upload, name='file_replace'),
	re_path(r'^file/remove/(?P<blog_id>\d{1,12})/(?P<file_id>\d{1,12})/$', views.file_remove, name='file_remove'),

	re_path(r'^comment/(?P<blog_pk>\d{1,12})/$', views.blog_comment, name='blog_comment'),
	re_path(r'^comment/delete/(?P<comment_pk>\d{1,12})/$', views.delete_blog_comment, name='blog_comment_delete'),

	re_path(r'^tag/view/$', views.tag_view, name='blog_tag'),
	re_path(r'^tag/view/(?P<tag>\d{1,12})/$', views.tag_view, name='blog_tag_view'),
	re_path(r'^tag/edit/$', views.tag_edit, name='blog_tag_add'),
	re_path(r'^tag/edit/(?P<pk>\d{1,12})/$', views.tag_edit, name='blog_tag_edit'),
	re_path(r'^tag/del/(?P<pk>\d{1,12})/$', views.tag_del, name='blog_tag_del'),

	re_path(r'^archive/$', views.archive, name='blog_archive'),
	re_path(r'^archive/(?P<year>\d{4})/$', views.archive, name='blog_archive_year'),
	re_path(r'^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.archive, name='blog_archive_month'),


]
