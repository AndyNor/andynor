#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Sum
from decimal import Decimal
from django.template import RequestContext
from django.http import Http404
from django.contrib.auth.decorators import login_required  # shortcut for is_authenticated()
from datetime import date, datetime
from django.contrib import messages  # Message system
from money.models import *
from mysite.site_wide_functions import get_previous_page, generate_form, makeJSON
from mysite.search import get_query
from django.urls import reverse
from django.views.decorators.cache import never_cache # avoid browser from caching content to disk
from django.middleware import csrf

APP_NAME = 'app_money'
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


# Generic object to store data
class Object(object):
	pass


def monthly_expences(request, year, month):

	if request.method == "POST":

		def day_to_date(year, month, day):
			return datetime(year=int(year), month=int(month), day=int(day))

		add_to_transaction(request=request, amount=-169, date=day_to_date(year, month, 24), sub_category=25, comment='Spotify')  # 25 Musikk
		add_to_transaction(request=request, amount=-139, date=day_to_date(year, month, 4), sub_category=23, comment='Netflix')  # 23 TV og serier
		add_to_transaction(request=request, amount=-430, date=day_to_date(year, month, 20), sub_category=12, comment='NOF innbo og reise')  # 12 Forskring bolig
		add_to_transaction(request=request, amount=-730, date=day_to_date(year, month, 20), sub_category=20, comment='FP Gruppeliv')  # 20 Forsikring helse
		add_to_transaction(request=request, amount=-29, date=day_to_date(year, month, 20), sub_category=21, comment='iCloud 200G')  #21 Internett
		add_to_transaction(request=request, amount=-750, date=day_to_date(year, month, 18), sub_category=84, comment='Ruter 30-dager')  # 84 Reise jobb
		add_to_transaction(request=request, amount=-99, date=day_to_date(year, month, 23), sub_category=23, comment='HBO Nordic')  # 23 TV og serier
		add_to_transaction(request=request, amount=-350, date=day_to_date(year, month, 17), sub_category=22, comment='Telenor (mobil + abb.)')  # 22 Telefon
		add_to_transaction(request=request, amount=-300, date=day_to_date(year, month, 15), sub_category=40, comment='Redd barna')  # 40 Veldedighet
		add_to_transaction(request=request, amount=-275, date=day_to_date(year, month, 20), sub_category=40, comment='Plan Norge')  # 40 Veldedighet
		add_to_transaction(request=request, amount=-215, date=day_to_date(year, month, 26), sub_category=58, comment='Audible')  # 58 Bøker
		add_to_transaction(request=request, amount=-799, date=day_to_date(year, month, 20), sub_category=17, comment='SATS')  # 17 Treningssenter
		add_to_transaction(request=request, amount=-519, date=day_to_date(year, month, 16), sub_category=21, comment='Get Internett')  # 21 Internett
		add_to_transaction(request=request, amount=-2693, date=day_to_date(year, month, 1), sub_category=90, comment='Fellesutgifter sameie MTG14')  # 90 fellesutgifter

		return HttpResponseRedirect(reverse("money_month", kwargs={'year': year, 'month': month}))

	else:
		return render(request, 'money_montly_expences.html', {
			'month_name': MONTH_NAMES[int(month) - 1],
			'month': month,
			'year': year,
			})

def add_to_transaction(request, amount, date, sub_category, comment):
	category = SubCategory.objects.get(pk=sub_category).parent_category
	account = Account.objects.get(pk=1)
	sub_category = SubCategory.objects.get(pk=sub_category)
	t = Transaction(
			owner=request.user,
			account=account,  # Lønn
			amount=amount,
			date=date,
			category=category,
			sub_category=sub_category,
			comment=comment,
			is_asset=False,
		)
	t.save()


# add account
def add_account(request, pk=False):
	user = request.user
	if pk:
		current_owner = Account.objects.get(pk=pk).owner
		if current_owner != user:
			messages.error(request, "You don't own this account!")
			return HttpResponseRedirect(reverse("money_admin_add_account"))
	account_form = generate_form(request, Account, AccountForm, pk, None)
	account_form.fields['sub_category'].choices = categories_as_choices(request.user)
	if account_form.is_valid():
		o = account_form.save(commit=False)
		o.owner = user
		o.save()
		return HttpResponseRedirect(reverse("money_admin_add_account"))

	entries = Account.objects.filter(owner=user).order_by('account_type') if (not pk) else None

	return render(request, 'money_edit.html', {
		'form': account_form,
		'entries': entries,
		'head_text': "Edit accounts"
	})


# add category
def category(request, pk=False):
	user = request.user
	if pk:
		current_owner = Category.objects.get(pk=pk).owner
		if current_owner != user:
			messages.error(request, "You don't own this category!")
			return HttpResponseRedirect(reverse("money_admin_category"))
	category_form = generate_form(request, Category, CategoryForm, pk, None)
	if category_form.is_valid():
		o = category_form.save(commit=False)
		o.owner = user
		o.save()
		return HttpResponseRedirect(reverse("money_admin_category"))

	entries = Category.objects.filter(owner=user) if (not pk) else None

	return render(request, 'money_edit.html', {
		'form': category_form,
		'entries': entries,
		'head_text': "Edit categories"
	})


# add subcategory
def subcategory(request, pk=False):
	user = request.user
	if pk:
		current_owner = SubCategory.objects.get(pk=pk).owner
		if current_owner != user:
			messages.error(request, "You don't own this subcategory!")
			return HttpResponseRedirect(reverse("money_admin_subcategory"))
	category_form = generate_form(request, SubCategory, SubCategoryForm, pk, None)
	category_form.fields['parent_category'].queryset = Category.objects.filter(owner=request.user)
	if category_form.is_valid():
		o = category_form.save(commit=False)
		o.owner = request.user
		o.save()
		return HttpResponseRedirect(reverse("money_admin_subcategory"))

	entries = SubCategory.objects.filter(owner=user).order_by('parent_category') if (not pk) else None

	return render(request, 'money_edit.html', {
		'form': category_form,
		'entries': entries,
		'head_text': "Edit subcategories"
	})


def categories_as_choices(user):
# http://dealingit.wordpress.com/2009/10/26/django-tip-showing-optgroup-in-a-modelform/
	categories = []
	for category in Category.objects.filter(owner=user):
		new_category = []
		sub_categories = []
		for sub_category in SubCategory.objects.filter(parent_category=category, owner=user):
			sub_categories.append([sub_category.id, sub_category.name])

		new_category = [category.name, sub_categories]
		categories.append(new_category)
	return categories


## Insert, update and delete stuff ##
@login_required
@never_cache
def edit(request, this_type, pk=False):

	try:
		request.user.profile
	except:
		messages.error(request, 'You need to create a user profile')
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	# Get the first account entry used as default choice in form
	try:
		Account.objects.filter(owner=request.user)[0].pk
	except:
		messages.error(request, "You have no accounts!")

	if pk:
		pk = int(pk)

	### salary
	if this_type == u'salary':

		if not pk:
			form = SalaryForm(initial={
				'account': request.user.profile.DEFAULT_PAYMENT_ACCOUNT,
				'comment': request.user.profile.DEFAULT_SALARY_COMMENT
			})
			if request.method == 'POST':
				form = SalaryForm(request.POST)
		else:
			try:
				instance = Salary.objects.get(pk=pk)
				if instance.owner != request.user:
					messages.error(request, "You don't own this salary registration!")
					return HttpResponseRedirect(reverse("money_new", args=["salary"]))
			except Salary.DoesNotExist:
				raise Http404
			form = SalaryForm(instance=instance)
			if request.method == 'POST':
				form = SalaryForm(request.POST, instance=instance)
		# Restrict options shown for account
		form.fields['account'].queryset = Account.objects.exclude(account_type=2).filter(owner=request.user)
		if request.method == 'POST':
			if form.is_valid():
				if form.cleaned_data:
					# new instance
					if not pk:
						# The salary is new
						s = form.save(commit=False)
						# Add the owner
						s.owner = request.user
						# Add a new transaction
						t = Transaction(
							owner=request.user,
							account=s.account,
							amount=s.amount(),
							date=s.date,
							sub_category=s.account.sub_category,
							category=s.account.sub_category.parent_category,
							comment=s.comment,
						)
						t.save()
						# Add the new transaction as foreign key
						s.transaction = t
						s.save()
					# edit existing instance
					else:
						# Update a salary, just save it
						s = form.save()
						# update the corresponding transaction
						t = s.transaction
						t.account = s.account
						t.amount = s.amount()
						t.date = s.date
						t.sub_category = s.account.sub_category
						t.category = s.account.sub_category.parent_category
						t.comment = s.comment
						t.save()

					return HttpResponseRedirect(get_previous_page(request, APP_NAME))
	### expence
	elif this_type == u'expence':

		if not pk:
			form = ExpenceForm(initial={
				'account': request.user.profile.DEFAULT_PAYMENT_ACCOUNT,
				'sub_category': request.user.profile.DEFAULT_EXPENCE_SUB_CATEGORY,
			})
			if request.method == 'POST':
				form = ExpenceForm(request.POST)
		else:
			try:
				instance = Transaction.objects.get(pk=pk)
				if instance.owner != request.user:
					messages.error(request, "You don't own this expence registration!")
					return HttpResponseRedirect(reverse("money_new", args=["expence"]))
			except Transaction.DoesNotExist:
				raise Http404
			form = ExpenceForm(instance=instance)
			if request.method == 'POST':
				form = ExpenceForm(request.POST, instance=instance)
		form.fields['sub_category'].choices = categories_as_choices(request.user)
		#form.fields['account'].queryset = Account.objects.exclude(account_type=2).filter(owner=request.user)
		form.fields['account'].queryset = Account.objects.filter(owner=request.user)
		if request.method == 'POST':
			if form.is_valid():
				if form.cleaned_data:
					if not pk:
						# The transaction is new
						t = form.save(commit=False)
						# Add the owner
						t.owner = request.user
						# Invert the sum (most used usecase)
						t.amount = -(t.amount)
						t.category = t.sub_category.parent_category
						t.save()
					else:
						# Updateing an existing transaction
						t = form.save(commit=False)
						# We can't invert the sum once again, but we check the category from subcategory
						t.category = t.sub_category.parent_category
						t.save()
					return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	### transaction
	elif this_type == u'transaction':

		form = TransactionForm(user=request.user)
		if request.method == 'POST':
			form = TransactionForm(request.POST, user=request.user)
		if form.is_valid():
			if form.cleaned_data:
				source_account = form.cleaned_data['source_account']
				destination_account = form.cleaned_data['destination_account']
				date_field = form.cleaned_data['date']
				amount = form.cleaned_data['amount']
				comment_remove = "Transferred to %s" % destination_account
				comment_add = "Transferred from %s" % source_account
				# Remove amount from account
				t1 = Transaction(
					owner=request.user,
					account=source_account,
					amount=-amount,
					comment=comment_remove,
					date=date_field,
					sub_category=destination_account.sub_category,
					category=destination_account.sub_category.parent_category,
				)
				t1.save()
				# Add to the destination account
				t2 = Transaction(
					owner=request.user,
					account=destination_account,
					amount=amount,
					comment=comment_add,
					date=date_field,
					sub_category=destination_account.sub_category,
					category=destination_account.sub_category.parent_category,
				)
				t2.save()
			return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	### downpayment
	elif this_type == u'downpayment':

		if not pk:
			form = DownpaymentForm(initial={
				# make it general !!
				'comment': request.user.profile.DEFAULT_DOWNPAYMENT_COMMENT,
				'source_account': request.user.profile.DEFAULT_PAYMENT_ACCOUNT,
			})
			if request.method == 'POST':
				form = DownpaymentForm(request.POST)
		else:
			try:
				instance = Downpayment.objects.get(pk=pk)
				if instance.owner != request.user:
					messages.error(request, "You don't own this loan repayment registration!")
					return HttpResponseRedirect(reverse("money_new", args=["downpayment"]))
			except Downpayment.DoesNotExist:
				raise Http404
			form = DownpaymentForm(instance=instance)
			if request.method == 'POST':
				form = DownpaymentForm(request.POST, instance=instance)
		form.fields['source_account'].queryset = Account.objects.exclude(account_type=2).filter(owner=request.user)
		form.fields['destination_account'].queryset = Account.objects.filter(account_type=2, owner=request.user)
		if request.method == 'POST':
			if form.is_valid():
				if form.cleaned_data:
					# new instance
					if not pk:
						# catch the new downpayment object
						d = form.save(commit=False)
						# remove money from source account
						t1 = Transaction(
							owner=request.user,
							account=d.source_account,
							amount=-(d.repayment + d.interest_and_fees),
							date=d.date,
							sub_category=d.destination_account.sub_category,
							category=d.destination_account.sub_category.parent_category,
							comment=d.comment,
						)
						t1.save()
						# add money to the receiving account
						t2 = Transaction(
							owner=request.user,
							account=d.destination_account,
							amount=d.repayment,
							date=d.date,
							sub_category=d.destination_account.sub_category,
							category=d.destination_account.sub_category.parent_category,
							comment=d.comment,
						)
						t2.save()
						# save the downpayment object
						d.owner = request.user
						d.source_transaction = t1
						d.destination_transaction = t2
						d.save()

					# edit existing instance
					else:
						# Update, just save it
						d = form.save()
						# update the corresponding transactions
						t1 = d.source_transaction
						t1.account = d.source_account
						t1.amount = -(d.repayment + d.interest_and_fees)
						t1.date = d.date
						t1.sub_category = d.destination_account.sub_category
						t1.category = d.destination_account.sub_category.parent_category
						t1.comment = d.comment
						t1.save()

						t2 = d.destination_transaction
						t2.account = d.destination_account
						t2.amount = d.repayment
						t2.date = d.date
						t2.sub_category = d.destination_account.sub_category
						t2.category = d.destination_account.sub_category.parent_category
						t2.comment = d.comment
						t2.save()

					return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	### default
	else:
		raise Http404

	# add text for headers
	head_text = "No title"
	if this_type == u'salary':
		head_text = "Add a new salary"
	if this_type == u'expence':
		head_text = "Register money spent"
	if this_type == u'transaction':
		head_text = "Transfer money between accounts"
	if this_type == u'downpayment':
		head_text = "Pay back a loan"

	return render(request, u'money_edit.html', {
		'type': this_type,
		'form': form,
		'back_link': request.session['redirect_url'],
		'head_text': head_text
	})


""" disabled cause one usually does not need to erase a transaction
@login_required
def remove(request, this_type, pk):
	pk = int(pk)

	### expence
	if this_type == u'expence':
		try:
			instance = Transaction.objects.get(pk=pk)
		except Transaction.DoesNotExist:
			raise Http404
		instance.delete()
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	### salary
	elif this_type == u'salary':
		try:
			instance = Salary.objects.get(pk=pk)
		except Salary.DoesNotExist:
			raise Http404
		# delete associated transaction
		t = instance.transaction
		t.delete()
		instance.delete()
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	### downpayment
	elif this_type == u'downpayment':
		try:
			instance = Downpayment.objects.get(pk=pk)
		except Downpayment.DoesNotExist:
			raise Http404
		# delete associated transactions
		t1 = instance.source_transaction
		t1.delete()
		t2 = instance.destination_transaction
		t2.delete()
		instance.delete()
		return HttpResponseRedirect(get_previous_page(request, APP_NAME))

	else:
		raise Http404
"""


## Show data in usefull ways ##
@login_required
@never_cache
def month(request, year, month):  # "2013/01"
	year = int(year)
	month = int(month)
	request.session['redirect_url'] = request.path

	def expence(request, year, month):
		table_data = Object()
		THEAD_COLS = [
			{u'text': u'Date', u'width': 10},
			{u'text': u'Account', u'width': 20},
			{u'text': u'Category', u'width': 30},
			{u'text': u'Expense', u'width': 10},
			{u'text': u'Income', u'width': 10},
			{u'text': u'Loan', u'width': 10},
			{u'text': u'Lend', u'width': 10},
		]
		# get all transactions matching user and period
		transactions = Transaction.objects.exclude(
			account__account_type=2,  # loan accaounts
		).filter(
			date__year=year,
			date__month=month,
			owner=request.user,
		).order_by(u'category', u'-date', u'-pk')
		# append some data
		details_sum = 0
		for t in transactions:
			details_sum += t.amount
			try:
				t.text_color = t.category.text_color
			except:
				pass
			# A transaction is considered loan/lend when in the future
			if t.date <= date.today():
				t.amount_income = t.amount if t.amount > 0 else ''
				t.amount_expense = t.amount if t.amount < 0 else ''
			else:
				t.amount_lend = t.amount if t.amount > 0 else ''
				t.amount_loan = t.amount if t.amount < 0 else ''

		table_data.thead = THEAD_COLS
		table_data.tbody = transactions
		table_data.sum = details_sum
		return table_data

	def salary(request, year, month):
		table_data = Object()
		THEAD_COLS = [
			{u'text': u'Date', u'width': 15},
			{u'text': u'Account', u'width': 25},
			{u'text': u'Salary', u'width': 12},
			{u'text': u'Extra hours', u'width': 12},
			{u'text': u'Tax', u'width': 12},
			{u'text': u'Retirement', u'width': 12},
			{u'text': u'Labor union', u'width': 12},
		]
		year = int(year)
		month = int(month)  # check valid year and month

		salary = Salary.objects.filter(
			date__year=year,
			date__month=month,
			owner=request.user,
		).order_by(u'account', u'date')

		table_data.thead = THEAD_COLS
		table_data.tbody = salary
		return table_data

	# Do the calculations
	expence_data = expence(request, year, month)
	salary_data = salary(request, year, month)

	def last_next_month(year, month):
		month_last = month - 1
		year_last = year
		if month_last == 0:
			month_last = 12
			year_last = year - 1

		month_next = month + 1
		year_next = year
		if month_next == 13:
			month_next = 1
			year_next = year + 1

		return {
			'last': {
				'month': month_last,
				'year': year_last,
			},
			'next': {
				'month': month_next,
				'year': year_next,
			}
		}

	return render(request, u'money_month.html', {
		'APP_NAME': APP_NAME,
		'year': year,
		'month': month,
		'month_name': MONTH_NAMES[month - 1],
		'sum': expence_data.sum,
		'expence_data': expence_data,
		'salary_data': salary_data,
		'links': last_next_month(year, month),
	})


@login_required
@never_cache
def details_income(request, year, month):
	request.session['redirect_url'] = request.path

	"""AUTO GENERATE"""
	THEAD_COLS = [
		{u'text': u'Date', u'width': 15},
		{u'text': u'Account', u'width': 25},
		{u'text': u'Extra hours', u'width': 12},
		{u'text': u'Labor union', u'width': 12},
		{u'text': u'Retirement', u'width': 12},
		{u'text': u'Salary', u'width': 12},
		{u'text': u'Tax', u'width': 12},
	]
	year = int(year)
	month = int(month)   # check valid year and month

	income = Salary.objects.filter(
		date__year=year,
		date__month=month,
		owner=request.user,
	).order_by(u'account', u'date')

	return render(request, u'details_income.html', {
		u'app_name': APP_NAME,
		u'thead': THEAD_COLS,
		u'year': year,
		u'income': income,
	})


@login_required
@never_cache
def year(request, year):  # "2013"
	request.session['redirect_url'] = request.path
	year = int(year)
	user = request.user

	def expence_data(request, year):
		data = []
		for cat in Category.objects.filter(owner=user).order_by(u'name'):
			cell_sums = []
			category_sum = Decimal(0)
			for month in range(0, 12):
				# do not show data from loan accounts
				sum = Transaction.objects.exclude(
					account__account_type=2,  # loan accaounts
				).filter(
					date__year=year,
					date__month=month + 1,
					owner=request.user,
					category=cat,
				).aggregate(value=Sum(u'amount'))[u'value']
				# sum all partial sums of this category
				if type(sum).__name__ == u'Decimal':
					category_sum += sum

				# group all partial sums per category
				cell_sums.append(sum)

			data.append({
				u'category': cat.name,
				u'cell_sums': cell_sums,
				u'category_sum': category_sum,
				u'text_color': cat.text_color,
			})
		data.append(month_sums(data))
		return data

	def salary_data(request, year):
		data = []
		for field_name in Salary._meta.get_fields():
			if field_name.get_internal_type() == u'DecimalField':
				cell_sums = []
				for month in range(0, 12):
					sum = Salary.objects.filter(
						owner=request.user,
						date__year=year,
						date__month=month + 1,
					).aggregate(sum=Sum(field_name.name))[u'sum']

					sum = Decimal(0) if sum is None else sum
					cell_sums.append(sum)

				category_sum = Decimal(0)
				for part_sum in cell_sums:
					if type(part_sum).__name__ == u'Decimal':
						category_sum += part_sum

				data.append({
					u'category': field_name.name.replace('_', ' '),
					u'cell_sums': cell_sums,
					u'category_sum': category_sum,
				})
		data.append(month_sums(data))
		return data

	def downpayment_data(request, year):
		"""AUTO GENERATE"""
		THEAD_COLS = [
			{u'text': u'Date', u'width': 5},
			{u'text': u'Source account', u'width': 35},
			{u'text': u'Destination account', u'width': 15},
			{u'text': u'Interest and fees', u'width': 15},
			{u'text': u'Repayment', u'width': 15},
			{u'text': u'Comment', u'width': 15},
		]
		payments = Downpayment.objects.filter(
			date__year=year,
			owner=request.user,
		).order_by(u'date')

		data = {'thead': THEAD_COLS, 'payments': payments}
		return data

	def month_sums(table_object):
		# Returns a list of the sums per month
		sums = []
		total = Decimal(0)
		for month in range(0, 12):
			local_sum = Decimal(0)
			for category in table_object:
				value_raw = category['cell_sums'][month]
				value = category['cell_sums'][month] if type(value_raw).__name__ == u'Decimal' else Decimal(0)
				local_sum += value
				total += value
			sums.append(local_sum)
		sums.append(total)
		return sums

	def assets(request, year):
		items = Transaction.objects.filter(
			owner=request.user,
			is_asset=True,
			date__year=year,
		).order_by('-date')
		# Invert amount from negative to positive
		for i in items:
			i.amount = -i.amount
		return items

	salary_data = salary_data(request, year)
	expence_data = expence_data(request, year)
	asset_data = assets(request, year)
	downpayment_data = downpayment_data(request, year)

	return render(request, u'money_year.html', {
		'month_names': MONTH_NAMES,
		'year': year,
		'next_year': year + 1,
		'last_year': year - 1,
		'expence_data': expence_data,
		'salary_data': salary_data,
		'dp_data': downpayment_data,
		'asset_data': asset_data,
	})


@login_required
@never_cache
def account(request, account, page):
	if page is None:
		page = 0

	num_per_page = 50

	page = int(page)
	start = num_per_page * page
	end = start + num_per_page

	def prepare_links(page):
		active = '' if (page != 0) else 'disabled'
		return {
			'last': {
				'page': page - 1 if (page > 0) else 0,
				'active': active
			},
			'next': {
				'page': page + 1,
			}
		}

	account_data = Object()
	t = Transaction.objects.filter(
		owner=request.user,
		account=account,
		# Only dates up until now
		#date__lte=date.today(),
	).order_by('-date', '-pk')[start:end]
	account_data.tbody = t

	account_name = Account.objects.get(pk=account).name

	return render(request, 'money_account.html', {
		'links': prepare_links(page),
		'table_data': account_data,
		'account': account_name,
		'account_id': account,
		'back_link': request.session['redirect_url'],
	})


"""
@login_required
def query(request):
	t = Transaction.objects.filter(
		owner=request.user,
		category=8,
	).order_by('-date')
	return render(request, u'money_account.html', {
		u'transactions': t,
	})
"""


def balance(request):
	accounts = Account.objects.filter(owner=request.user).order_by("description")
	account_balance = []
	sum_real = Decimal(0)
	sum_planned = Decimal(0)
	for a in accounts:
		real_balance = Transaction.objects.filter(
			owner=request.user,
			account=a.pk,
			# Only dates up until now
			date__lte=date.today(),
		).aggregate(sum=Sum('amount'))['sum']

		planned_balance = Transaction.objects.filter(
			owner=request.user,
			account=a.pk,
		).aggregate(sum=Sum('amount'))['sum']

		account_balance.append({
			'pk': a.pk,
			'account': a.name,
			'real': real_balance,
			'planned': planned_balance,
		})
		if real_balance is not None:
			sum_real += real_balance
		if planned_balance is not None:
			sum_planned += planned_balance


	return {
		"data": account_balance,
		"sum_real": sum_real,
		"sum_planned": sum_planned
	}


@login_required
@never_cache
def search(request):
	from django.db.models import Sum
	query = request.GET.get('q', None)
	if query:
		entry_query = get_query(query, ['comment', 'category__name', 'sub_category__name'])
		if entry_query is not None:
			found_entries = Transaction.objects.filter(
				entry_query,
				owner=request.user
			).order_by('-date')
			query_sum = found_entries.aggregate(sum_total=Sum('amount'))

			return render(request, 'money_search.html', {
				'query_string': query,
				'found_entries': found_entries,
				'query_sum': query_sum
			})

		else:
			return render(request, 'money_search.html', {
				'query_string': query,
				'found_entries': None,
			})
	else:
		messages.error(request, 'No serach query!')
		return render(request, 'money_search.html', {
			'query_string': query,
			'found_entries': None,
		})


@login_required
@never_cache
def index(request):
	request.session['redirect_url'] = request.path

	def year_summary(request):
		year_data = []
		unique_years = Transaction.objects.filter(owner=request.user).dates('date', 'year').reverse()
		for datetime_year in unique_years: #[:20]
			year = int(datetime_year.year)
			salaries = Salary.objects.filter(
				owner=request.user,
				date__year=year,
			)
			gross = nett = tax = retirement = 0
			for s in salaries:
				gross += s.salary + s.extra_hours
				nett += s.amount()
				tax += s.tax
				retirement += s.retirement_pension
			retirement = - retirement
			tax = - tax
			tax_pct = (tax / gross) if gross != 0 else 0

			year_data.append({
				u'year': year,
				u'gross': gross,
				u'nett': nett,
				u'tax': tax,
				u'tax_pct': round(tax_pct * 100, 1),
				u'retirement': retirement,
			})
		return year_data

	balance_data = balance(request)
	year_data = year_summary(request)

	return render(request, u'money_index.html', {
		'balance_data': balance_data,
		'balance_json': makeJSON(balance_data["data"]),
		'year_data': year_data,
		'year_json': makeJSON(year_data),
		'APP_NAME': APP_NAME,
	})
