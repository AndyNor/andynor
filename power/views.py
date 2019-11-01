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
		"""
		payment = {
			'timestamp': montly_timestamp(p.date),
			'cost': round(float(p.cost_day), 2),
			'usage': round(float(p.kwh_usage / days_of_month), 2),
			'price': round(float(p.kwh_usage_cost * 100), 4),
		}
		"""
		timestamp = int(montly_timestamp(p.date))
		forbruk["kwh_pris"].append(round(float(p.kwh_usage_cost * 100), 4))
		forbruk["antall_kwh"].append(round(float(p.kwh_usage / days_of_month), 2))
		year = int(p.date.strftime('%Y'))
		month = int(p.date.strftime('%m'))
		kwh = round(float(p.kwh_usage / days_of_month), 2)
		if not year in forbruk_monthly:
			forbruk_monthly[year] = {}
		forbruk_monthly[year][month] = kwh

		"""
		cost_parts = {
			'timestamp': timestamp,
			'usage': round(float(p.kwh_usage * p.kwh_usage_cost), 2),
			'cable': round(float(p.kwh_usage * p.kwh_rent_cost), 2),
			'static': round(float(p.fixed_cost), 2),
		}
		"""
		usage = round(float(p.kwh_usage * p.kwh_usage_cost), 2)
		cable = round(float(p.kwh_usage * p.kwh_rent_cost), 2)
		static = round(float(p.fixed_cost), 2)
		#total_cost["labels"].append(int(time.mktime(p.date.timetuple())))
		total_cost["labels"].append(timestamp)
		total_cost["usage"].append(usage)
		total_cost["grid"].append(cable)
		total_cost["static"].append(static)

		payments_json_data.append(payment)
		#total_cost_data.append(cost_parts)

	forbruk["labels"] = total_cost["labels"]

	for year in forbruk_monthly:
		current_values = []
		for month in range(1,13):  # 13 is not included in the range btw
			if not month in forbruk_monthly[year]:
				forbruk_monthly[year][month] = 0


	#payments_json = json.dumps(payments_json_data)

	#readings = models.Reading.objects.filter(owner=owner).order_by('-pk')
	#readings_json_data = []
	"""
	for r in readings:
		timestamp = time.mktime(r.date.timetuple())
		reading = {
			'timestamp': timestamp,
			'kwh': round(float(r.daily_usage), 2)
		}
		readings_json_data.append(reading)
	"""
	#readings_json = json.dumps(readings_json_data)
	#total_cost_data_json = json.dumps(total_cost_data)

	return render(request, 'power.html', {
		#'payments_json': payments_json,
		#'readings_json': readings_json,
		#'total_cost_json': total_cost_data_json,
		'total_cost': total_cost,
		'forbruk': forbruk,
		'forbruk_monthly': sorted(forbruk_monthly.items()),
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
				messages.error(request, "That payment is not yours!")
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


@login_required
def reading(request):
	reading_form = models.ReadingForm()
	if request.method == 'POST':
		reading_form = models.ReadingForm(request.POST)
		if reading_form.is_valid():
			earlier_readings = models.Reading.objects.filter(owner=request.user)

			# this is the first registration
			if not earlier_readings:
				messages.success(request, "Congratulations on the first reading!")
				f = reading_form.save(commit=False)
				f.owner = request.user
				f.period_usage = 0
				f.daily_usage = 0
				f.save()
				return HttpResponseRedirect(get_previous_page(request, APP_NAME))

			# a normal registration
			else:
				last_reading = earlier_readings.latest('id')

				this_kwh = reading_form.cleaned_data['kwh']
				this_date = reading_form.cleaned_data['date']

				if last_reading.date >= this_date:
					messages.error(request, "You already got a later registration!")
					return HttpResponseRedirect(reverse("power_reading"))

				if last_reading.kwh > this_kwh:
					messages.error(request, "Your last registration was higher!")
					return HttpResponseRedirect(reverse("power_reading"))

				last_kwh = last_reading.kwh
				last_date = last_reading.date
				last_period_usage = last_reading.period_usage

				time_delta = this_date - last_date

				f = reading_form.save(commit=False)
				f.owner = request.user
				f.period_usage = (this_kwh - last_kwh) + last_period_usage
				try:
					f.daily_usage = round(float(f.period_usage - last_period_usage) / time_delta.days)
				except:
					f.daily_usage = 0
				f.save()
				return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	readings = models.Reading.objects.filter(owner=request.user).order_by('-pk')

	return render(request, 'power_reading.html', {
		'reading_form': reading_form,
		'readings': readings,
	})


@login_required
def reading_reset(request, new_state=0):
	new_state = int(new_state)
	r = models.Reading(
		owner=request.user,
		date=models.Reading.objects.filter(owner=request.user).latest('id').date,
		kwh=new_state,
		period_usage=0,
		daily_usage=0)
	r.save()
	return HttpResponseRedirect(get_previous_page(request, APP_NAME))
