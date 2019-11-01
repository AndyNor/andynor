from django.conf.urls import url
from stocks import views

urlpatterns = [
	url(r'^$', views.index, name='app_stocks'),
	url(r'^ticker/(?P<ticker>\d{1,12})/$', views.details, name='stocks_details'),

	url(r'^ticker/split/(?P<pk>\d{1,12})/$', views.split_ticker, name='stocks_split_ticker'),
	url(r'^ticker/merge/(?P<pk>\d{1,12})/$', views.merge_ticker, name='stocks_merge_ticker'),
	
	url(r'^transaction/new/$', views.write_transaction, name='stocks_transaction_new'),
	url(r'^transaction/edit/(?P<pk>\d{1,12})/$', views.write_transaction, name='stocks_transaction_edit'),
	url(r'^transaction/remove/(?P<pk>\d{1,12})/$', views.remove_transaction, name='stocks_transaction_remove'),

	url(r'^ticker/new/$', views.write_ticker, name='stocks_ticker_new'),
	url(r'^ticker/edit/(?P<pk>\d{1,12})/$', views.write_ticker, name='stocks_ticker_edit'),
	url(r'^ticker/remove/(?P<pk>\d{1,12})/$', views.remove_ticker, name='stocks_ticker_remove'),

	url(r'^markedprice/new/$', views.write_ticker_history, name='stocks_ticker_history_new'),
	url(r'^markedprice/edit/(?P<pk>\d{1,12})/$', views.write_ticker_history, name='stocks_ticker_history_edit'),
]