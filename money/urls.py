from django.conf.urls import url
import datetime
from money import views

#now = datetime.datetime.now()

urlpatterns = [
	url(r'^api/sync/$', views.sbanken_sync, name="sbanken_sync"),
	#url(r'^api/accounts/$', views.sbanken_accounts, name="sbanken_accounts"),
	#url(r'^api/transactions/(?P<accountID>[A-F0-9]{32})/$', views.sbanken_transactions, name="sbanken_transactions"),
	url(r'^bank/transactions/$', views.bank_transactions, name="bank_transactions"),
	url(r'^create/(?P<bank_transaction>\d{1,10})/$', views.create_transaction, name="create_transaction"),
	url(r'^migrate/(?P<bank_transaction>\d{1,10})/$', views.migrate, name="money_migrate"),
	url(r'^edit/(?P<this_type>[a-z_]{1,20})/$', views.edit, name="money_new"),
	url(r'^edit/(?P<this_type>[a-z_]{1,20})/(?P<pk>\d{1,12})/$', views.edit, name="money_edit"),
	url(r'^admin/category(?:/(?P<pk>\d{1,10}))?/$', views.category, name="money_admin_category"),
	url(r'^admin/account(?:/(?P<pk>\d{1,10}))?/$', views.add_account, name="money_admin_add_account"),
	url(r'^admin/subcategory(?:/(?P<pk>\d{1,10}))?/$', views.subcategory, name="money_admin_subcategory"),
	#url(r'^remove/(?P<this_type>[a-z]{1,11})/(?P<pk>\d{1,12})/$', 'remove'),
	url(r'^account/(?P<account>\d{1,5})(?:/(?P<page>\d{1,10}))?/$', views.account, name="money_account"),
	url(r'^(?P<year>\d{4})/$', views.year, name="money_year"),
	url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.month, name="money_month"),
	url(r'^monthly_fixed/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.monthly_expences, name="money_add_monthly_expences"),
	url(r'^search/$', views.search, name="money_search"),
	url(r'^$', views.index, name="app_money"),
]
