from django.urls import include, re_path
from stocks import views

urlpatterns = [
	re_path(r'^$', views.index, name='app_stocks'),
	re_path(r'^ticker/(?P<ticker>\d{1,12})/$', views.details, name='stocks_details'),

	re_path(r'^ticker/split/(?P<pk>\d{1,12})/$', views.split_ticker, name='stocks_split_ticker'),
	re_path(r'^ticker/merge/(?P<pk>\d{1,12})/$', views.merge_ticker, name='stocks_merge_ticker'),
	
	re_path(r'^transaction/new/$', views.write_transaction, name='stocks_transaction_new'),
	re_path(r'^transaction/edit/(?P<pk>\d{1,12})/$', views.write_transaction, name='stocks_transaction_edit'),
	re_path(r'^transaction/remove/(?P<pk>\d{1,12})/$', views.remove_transaction, name='stocks_transaction_remove'),

	re_path(r'^ticker/new/$', views.write_ticker, name='stocks_ticker_new'),
	re_path(r'^ticker/edit/(?P<pk>\d{1,12})/$', views.write_ticker, name='stocks_ticker_edit'),
	re_path(r'^ticker/remove/(?P<pk>\d{1,12})/$', views.remove_ticker, name='stocks_ticker_remove'),

	re_path(r'^markedprice/new/$', views.write_ticker_history, name='stocks_ticker_history_new'),
	re_path(r'^markedprice/edit/(?P<pk>\d{1,12})/$', views.write_ticker_history, name='stocks_ticker_history_edit'),
]