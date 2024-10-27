#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from stocks.models import Transaction, Ticker, TickerHistory, TransactionForm, TickerForm, TickerHistoryForm
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from copy import deepcopy
import datetime
from django.db.models import Sum
from mysite.site_wide_functions import get_previous_page, generate_form, set_redirect_session, safe_referrer
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.middleware import csrf
from django.contrib.auth.decorators import permission_required

APP_NAME = 'stocks'

@permission_required('stocks.transaction.can_add_transaction', raise_exception=True)
def index(request):
	view_data_summary = []
	unique_tickers = Ticker.objects.all()
	view_data_estimate_sum = 0
	view_data_current_value_sum = 0
	view_data_gebyrer_sum = 0
	#view_data_money_compare = 0  # for comparison with "money app stocks account"
	for ticker in unique_tickers:
		try:
			current_price = TickerHistory.objects.filter(ticker=ticker).order_by('-date')[:1].get()
			current_price_value = current_price.price
		except:
			current_price = None
			current_price_value = Decimal(0) # default value

		sum_amount = Decimal(0)
		sum_total_price = Decimal(0)
		sum_brokerage = Decimal(0)

		transactions = Transaction.objects.filter(ticker=ticker)
		for t in transactions:
			sum_amount += t.amount
			sum_total_price += t.total_price - t.brokerage
			sum_brokerage += t.brokerage

		estimate = (sum_amount * current_price_value) - sum_total_price
		view_data_estimate_sum += estimate

		if sum_amount < 1:
			average_stock_price = None
		else:
			average_stock_price = (sum_total_price - sum_brokerage) / sum_amount

		try:
			current_value = sum_amount * current_price.price
		except:
			current_value = 0

		view_data_current_value_sum += current_value
		view_data_gebyrer_sum += sum_brokerage

		view_data_summary.append({
				'ticker': ticker,
				'sum_amount': sum_amount,
				'sum_total_price': sum_total_price,
				'current_price': current_price,
				'sum_brokerage': sum_brokerage,
				'average_stock_price': average_stock_price,
				'estimate': estimate,
				'current_value': current_value
			})

	view_data_tax = {}
	result_data = {}
	unique_years = []
	summary_year = {}
	sum_of_sums = 0
	for ticker in unique_tickers:
		ticker_fifo_match = fifo_match(request, ticker)
		ticker_data = {}
		for transaction in ticker_fifo_match:
			if transaction['sold'] != None:
				year = transaction['sold'].date.year
				if year not in unique_years:
					unique_years.append(year)
				result = (transaction['sold'].average_stock_price - transaction['bought'].average_stock_price) * transaction['sold'].amount
				try:
					ticker_data[year] += result
				except KeyError:
					ticker_data[year] = result
				try:
					summary_year[year] += result
				except KeyError:
					summary_year[year] = result

		result_data[ticker] = ticker_data

	for year in summary_year:
		sum_of_sums += summary_year[year]


	brokerage_sum = {}
	for year in unique_years:
		# minus because it is an expence, brokerage__sum is the key in the returned query
		brokerage_sum[year] = -Transaction.objects.filter(date__year=year).aggregate(Sum('brokerage'))['brokerage__sum']
		try:
			summary_year[year] += brokerage_sum[year]
		except:
			summary_year[year] = brokerage_sum[year]

	ticker_sums = {}
	for key, values in result_data.items():
		ticker_sum = 0
		for k, v in values.items():
			ticker_sum += v
		ticker_sums[key] = ticker_sum

	#print(ticker_sums)


	view_data_tax['years'] = sorted(unique_years)  # show only the 10 last years (only applies in template)
	view_data_tax['result_data'] = result_data
	view_data_tax['brokerage'] = brokerage_sum
	view_data_tax['total_sum'] = summary_year

	return render(request, 'stocks.html', {
			'view_data_summary': view_data_summary,
			'view_data_estimate_sum': view_data_estimate_sum,
			'view_data_current_value_sum': view_data_current_value_sum,
			'view_data_gebyrer_sum': view_data_gebyrer_sum,
			'view_data_tax': view_data_tax,
			'sum_of_sums': sum_of_sums,
			'ticker_sums': ticker_sums,
		 })

@permission_required('stocks.transaction.can_add_transaction', raise_exception=True)
def details(request, ticker):
	view_data = []
	result_total = 0
	try:
		ticker_object = Ticker.objects.get(id=ticker)
		header_text = {'name': ticker_object.company_name, 'ticker': ticker_object.ticker_name}
		view_data = fifo_match(request, ticker_object)
		for i in view_data:
			try:
				result = (i['sold'].average_stock_price - i['bought'].average_stock_price) * i['sold'].amount
				result_total += result
			except:
				result = None
			i['result'] = result

		graph_num_stocks = []
		graph_cost_stocks = []
		graph_value_stocks = []
		graph_labels = []

		num_stocks = 0
		cost_stocks = 0
		value_stocks = 0
		date_tracker = None
		total_stocks = 0

		transactions = Transaction.objects.filter(ticker=ticker_object).order_by('date')
		for t in transactions:
			if date_tracker == None:
				date_tracker = t.date.isoformat()

			num_stocks += t.amount
			cost_stocks += t.total_price
			value_stocks = num_stocks * round(((t.total_price - t.brokerage) / t.amount), 2)

			if t.date.isoformat() != date_tracker:
				graph_num_stocks.append(int(num_stocks))
				graph_cost_stocks.append(int(cost_stocks))
				graph_value_stocks.append(int(value_stocks))
				graph_labels.append(t.date.isoformat())

			date_tracker = t.date.isoformat()


		#nåverdi
		if num_stocks != 0:
			try:
				latest_price = TickerHistory.objects.filter(ticker=ticker_object).order_by('date')[0].price
			except:
				latest_price = 0

			graph_num_stocks.append(int(num_stocks)) #the same
			graph_cost_stocks.append(int(cost_stocks)) #the same
			graph_value_stocks.append(int(num_stocks * latest_price)) # current ticker price times the amount
			graph_labels.append(datetime.date.today().isoformat())


	except ObjectDoesNotExist:
		set_redirect_session(request, 'app_stocks', {})
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	return render(request, 'stocks_details.html', {
			'view_data': view_data,
			'result_total': result_total,
			'header_text': header_text,
			'graph_num_stocks': graph_num_stocks,
			'graph_cost_stocks': graph_cost_stocks,
			'graph_value_stocks': graph_value_stocks,
			'graph_labels': graph_labels,
		})


def fifo_match(request, ticker_object):
	# transactions must have newest first
	transactions = Transaction.objects.filter(ticker=ticker_object).order_by('-date')
	bought = []
	sold = []
	# group buy and sell in two lists (they are last-in, first-out)
	for t in transactions:
		t.average_stock_price = (t.total_price - t.brokerage) / t.amount
		if t.amount < 0:
			# negative sign in not interesting in this context
			t.amount = -t.amount
			t.total_price = -t.total_price
			sold.append(t)
		else:
			bought.append(t)
	# match sell with buy FIFO - First Inn First Out
	# oldest was the last to be pushed to the list
	fifo_list = []
	while len(sold) != 0:
		s = sold.pop()
		try:
			b = bought.pop()
		except IndexError:
			error_message = u'Logisk feil: Det er solgt aksjer i %s som du ikke har eid.' % (s.ticker.company_name)
			messages.error(request, error_message)
			pass
		if s.amount == b.amount:
			# add both b and s to output
			fifo_list.append({'bought': b, 'sold': s})
		elif s.amount > b.amount:
			# add b to output, split s, add b-part of s to output and put rest back to sold
			s_rest = deepcopy(s)
			s_rest.amount -= b.amount
			# note we don't use total_price or brokerage for anything, and we don't store anything new
			sold.append(s_rest)
			s.amount = b.amount
			fifo_list.append({'bought': b, 'sold': s})
		else:  # s.amount < b.amount
			# add s to output, split b, add s-part of b to output and put rest back to bought
			b_rest = deepcopy(b)
			b_rest.amount -= s.amount
			bought.append(b_rest)
			b.amount = s.amount
			fifo_list.append({'bought': b, 'sold': s})
	while len(bought) != 0:
		b = bought.pop()
		fifo_list.append({'bought': b, 'sold': None})
	return fifo_list


@permission_required('stocks.transaction.can_change_transaction', raise_exception=True)
def write_transaction(request, pk=False):
	transaction_form = generate_form(request, Transaction, TransactionForm, pk)
	if transaction_form.is_valid():
		tf = transaction_form.save()
		messages.success(request, u'Transaction added/updated with ID=%s' % tf.pk)
		set_redirect_session(request, 'app_stocks', {})
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	if pk:
		request.session['redirect_next'] = safe_referrer(request)
		try:
			header_text = "Redigere transaksjon"
			delete_link_pk = pk
			redirect_url = None
		except:
			return Http404
	else:
		header_text = u'Ny transaksjon'
		redirect_url = None
		delete_link_pk = False

	return render(request, 'stocks_edit.html', {
		u'form': transaction_form,
		u'header_text': header_text,
		u'redirect': redirect_url,
		u'delete_link_name': "stocks_transaction_remove",
		u'delete_link_pk': delete_link_pk,
	})

@permission_required('stocks.ticker.can_add_ticker', raise_exception=True)
def write_ticker(request, pk=False):
	ticker_form = generate_form(request, Ticker, TickerForm, pk)
	if ticker_form.is_valid():
		tf = ticker_form.save()
		messages.success(request, u'Ticker added/updated with ID=%s' % tf.pk)
		set_redirect_session(request, 'app_stocks', {})
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	if pk:
		request.session['redirect_next'] = safe_referrer(request)
		try:
			header_text = "Redigere ticker"
			delete_link_pk = pk
			redirect_url = None
		except:
			return Http404
	else:
		header_text = u'Ny ticker'
		redirect_url = None
		delete_link_pk = False

	return render(request, 'stocks_edit.html', {
		u'form': ticker_form,
		u'header_text': header_text,
		u'redirect': redirect_url,
		u'delete_link_name': "stocks_ticker_remove",
		u'delete_link_pk': delete_link_pk,
	})

@permission_required('stocks.ticker_history.can_add_ticker_history', raise_exception=True)
def write_ticker_history(request, pk=False):
	ticker_form = generate_form(request, TickerHistory, TickerHistoryForm, pk)
	if ticker_form.is_valid():
		tf = ticker_form.save()
		messages.success(request, u'Ticker history added/updated with ID=%s' % tf.pk)
		set_redirect_session(request, 'app_stocks', {})
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	if pk:
		request.session['redirect_next'] = safe_referrer(request)
		try:
			header_text = "Redigere markedspris"
			delete_link_pk = pk
			redirect_url = None
		except:
			return Http404
	else:
		header_text = u'Ny markedspris'
		redirect_url = None
		delete_link_pk = None

	return render(request, 'stocks_edit.html', {
		u'form': ticker_form,
		u'header_text': header_text,
		u'redirect': redirect_url,
		u'delete_link_name': "stocks_ticker_remove",
		u'delete_link_pk': delete_link_pk,
	})

@permission_required('stocks.transaction.can_remove_transaction', raise_exception=True)
def remove_transaction(request, pk):
	csrf_token = csrf.get_token(request)
	request_token = request.GET.get('token')
	if request_token == csrf_token:
		t = Transaction.objects.get(pk=pk)
		t.delete()
		messages.success(request, u'Transaction with ID=%s was deleted' % pk)
		set_redirect_session(request, 'app_stocks', {})
	else:
		messages.error(request, u'Token did not match')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))

@permission_required('stocks.ticker.can_remove_ticker', raise_exception=True)
def remove_ticker(request, pk):
	csrf_token = csrf.get_token(request)
	request_token = request.GET.get('token')
	if request_token == csrf_token:
		t = Ticker.objects.get(pk=pk)
		t.delete()
		messages.success(request, u'Ticker with ID=%s was deleted' % pk)
		set_redirect_session(request, 'app_stocks', {})
	else:
		messages.error(request, u'Token did not match')

	return HttpResponseRedirect(get_previous_page(request, APP_NAME))



@permission_required('stocks.ticker.can_remove_ticker', raise_exception=True)
def split_ticker(request, pk):
	stock_name = Ticker.objects.get(pk=pk).company_name
	description = "Split stocks for %s" % (stock_name)

	if request.method == "POST":
		split_ratio = int(request.POST.get('split_ratio'))
		if split_ratio <= 0:
			messages.error(request, "Can't split with negative numbers")
			return HttpResponseRedirect(reverse('app_stocks', args=[]))
		t_all = Transaction.objects.filter(ticker_id=pk)
		for t in t_all:
			t.amount = (t.amount * split_ratio)
			t.save()
		success_message = u'Split of 1 to %s complete' % (split_ratio)
		messages.success(request, success_message)
		return HttpResponseRedirect(reverse('app_stocks', args=[]))
	else:
		return render(request, 'stocks_split.html', {
			u'description': description
		})




@permission_required('stocks.ticker.can_remove_ticker', raise_exception=True)
def merge_ticker(request, pk):
	stock_name = Ticker.objects.get(pk=pk).company_name
	description = "Merge stocks for %s" % (stock_name)

	if request.method == "POST":
		merge_ratio = int(request.POST.get('merge_ratio'))
		if merge_ratio <= 0:
			messages.error(request, "Can't split with negative numbers")
			return HttpResponseRedirect(reverse('app_stocks', args=[]))
		t_all = Transaction.objects.filter(ticker_id=pk)
		for t in t_all:
			t.amount = (t.amount / merge_ratio)
			t.save()
		success_message = u'Merge of %s to 1 complete' % merge_ratio
		messages.success(request, success_message)
		return HttpResponseRedirect(reverse('app_stocks', args=[]))
	else:
		return render(request, 'stocks_merge.html', {
			u'description': description
		})