from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect  # redirect after successfull POST
from django.template import RequestContext  # required for csrf
from django.contrib.auth.decorators import login_required  # shortcut for is_authenticated()
from django.contrib.auth.decorators import permission_required
from power import models
from django.contrib.auth.models import User
from datetime import date, datetime
import time
import json  # used for json export
from mysite.site_wide_functions import get_previous_page, generate_form
from django.contrib import messages  # Message system

APP_NAME = 'app_power'

def day_of_month(datetime_date):
	this_year = int(datetime_date.strftime('%Y'))
	this_month = int(datetime_date.strftime('%m'))
	next_year = this_year
	next_month = this_month + 1
	if next_month > 12:
		next_year = next_year + 1
		next_month = 1
	return (date(next_year, next_month, 1) - date(this_year, this_month, 1)).days


def montly_timestamp(datetime_date):
	this_year = int(datetime_date.strftime('%Y'))
	this_month = int(datetime_date.strftime('%m'))
	midway = int(day_of_month(datetime_date) / 2)
	new_datetime = datetime(this_year, this_month, midway)
	return time.mktime(new_datetime.timetuple())


def index(request):
	if request.user.is_authenticated:
		owner = request.user
	else:
		owner = 1  # user "andre"

	payments = models.Payment.objects.filter(owner=owner).order_by('date')
	payments_json_data = []
	total_cost_data = []
	total_cost = {"labels": [], "usage": [], "grid": [], "static": []}
	forbruk = {"labels": [], "kwh_pris": [], "antall_kwh": []}
	forbruk_monthly = {}

	for p in payments:
		p.cost_total = p.cost_total()
		days_of_month = day_of_month(p.date)
		p.cost_day = p.cost_total / days_of_month
		''' Date is rounded to the closest month and Decimal must be converted to float '''

		timestamp = int(montly_timestamp(p.date))
		forbruk["kwh_pris"].append(round(float(p.kwh_usage_cost * 100), 4))
		forbruk["antall_kwh"].append(round(float(p.kwh_usage / days_of_month), 2))
		year = int(p.date.strftime('%Y'))
		month = int(p.date.strftime('%m'))
		kwh = round(float(p.kwh_usage / days_of_month), 2)
		if not year in forbruk_monthly:
			forbruk_monthly[year] = {}
		forbruk_monthly[year][month] = kwh

		usage = round(float(p.kwh_usage * p.kwh_usage_cost), 2)
		cable = round(float(p.kwh_usage * p.kwh_rent_cost), 2)
		static = round(float(p.fixed_cost), 2)
		total_cost["labels"].append(timestamp)
		total_cost["usage"].append(usage)
		total_cost["grid"].append(cable)
		total_cost["static"].append(static)

		payments_json_data.append(payment)

	forbruk["labels"] = total_cost["labels"]

	for year in forbruk_monthly:
		current_values = []
		for month in range(1,13):  # 13 != included in the range btw
			if not month in forbruk_monthly[year]:
				forbruk_monthly[year][month] = 0

	sortert_forbruk_monthly = {}
	for year in forbruk_monthly:
		sortert_forbruk_monthly[year] = {k: v for k, v in sorted(forbruk_monthly[year].items(), key=lambda item: item[0])}


	return render(request, 'power.html', {
		'total_cost': total_cost,
		'forbruk': forbruk,
		'forbruk_monthly': sortert_forbruk_monthly.items(),
	})


@login_required
def payment(request, pk=False):
	initial = {
		'kwh_rent_cost': 0.34,
		'fixed_cost': 334,
	}
	if pk:
		try:
			if models.Payment.objects.get(pk=pk).owner != request.user:
				messages.error(request, "That payment != yours!")
				return HttpResponseRedirect(get_previous_page(request, APP_NAME))
		except:
			messages.error(request, "That payment does not exists!")
			return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	payment_form = generate_form(request, models.Payment, models.PaymentForm, pk, initial)
	if payment_form.is_valid():
		p = payment_form.save(commit=False)
		p.owner = request.user
		p.save()
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	payments = models.Payment.objects.filter(owner=request.user).order_by('-date')

	return render(request, 'power_payment.html', {
		'payment_form': payment_form,
		'payments': payments,
	})
