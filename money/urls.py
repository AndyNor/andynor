from django.urls import include, re_path
import datetime
from money import views

urlpatterns = [
	re_path(r'^api/sync/$', views.sbanken_sync, name="sbanken_sync"),
	re_path(r'^bank/transactions/$', views.bank_transactions, name="bank_transactions"),
	re_path(r'^create/(?P<bank_transaction>\d{1,10})/$', views.create_transaction, name="create_transaction"),
	re_path(r'^migrate/(?P<bank_transaction>\d{1,10})/$', views.migrate, name="money_migrate"),
	re_path(r'^edit/(?P<this_type>[a-z_]{1,20})/$', views.edit, name="money_new"),
	re_path(r'^edit/(?P<this_type>[a-z_]{1,20})/(?P<pk>\d{1,12})/$', views.edit, name="money_edit"),
	re_path(r'^admin/category(?:/(?P<pk>\d{1,10}))?/$', views.category, name="money_admin_category"),
	re_path(r'^admin/account(?:/(?P<pk>\d{1,10}))?/$', views.add_account, name="money_admin_add_account"),
	re_path(r'^admin/subcategory(?:/(?P<pk>\d{1,10}))?/$', views.subcategory, name="money_admin_subcategory"),
	re_path(r'^account/(?P<account>\d{1,5})(?:/(?P<page>\d{1,10}))?/$', views.account, name="money_account"),
	re_path(r'^(?P<year>\d{4})/$', views.year, name="money_year"),
	re_path(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.month, name="money_month"),
	re_path(r'^monthly_fixed/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.monthly_expences, name="money_add_monthly_expences"),
	re_path(r'^search/$', views.search, name="money_search"),
	re_path(r'^$', views.index, name="app_money"),
]
