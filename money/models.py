# coding=UTF-8
from django.db import models
from django import forms
from django.contrib.auth.models import User
from mysite.models import make_custom_plugins
from datetime import datetime
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MONEY_MAX_DIGITS = 15
MONEY_DECIMAL_PLACES = 2


class Category(models.Model):
# Used for color coding in summary
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	name = models.CharField(max_length=25)
	text_color = models.CharField(max_length=6, blank=True)
	description = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return u'%s' % (self.name)


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		exclude = ('owner',)

	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		self.fields['text_color'].widget.attrs['class'] = 'color'


class SubCategory(models.Model):
# Sub categories are required. They link back to a generic category
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	name = models.CharField(max_length=25)
	parent_category = models.ForeignKey(Category, on_delete=models.PROTECT)
	description = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return u'%s' % (self.name)


class SubCategoryForm(forms.ModelForm):
	class Meta:
		model = SubCategory
		exclude = ('owner',)


class Account(models.Model):
# Every transaction are liked to an account
	ACCOUNT_TYPE_CHOISES = (
		(u'0', u'Expence'),  # Expence account from where you pay for goods
		(u'1', u'Saving'),  # Savings account you don't pay directly with. Usually with higher interest
		(u'2', u'Loan'),  # Loan accounts. Mortgage loans like car and house
	)
	owner = models.ForeignKey(User, on_delete=models.PROTECT)  # Unique per user
	name = models.CharField(max_length=25)
	# Account type is used when making transactions.
	account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPE_CHOISES)
	sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
	description = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return u'%s' % (self.name)

class AccountForm(forms.ModelForm):

	class Meta:
		model = Account
		exclude = ('owner',)


def validate_lovlig_dato(value):
	if not (value >= 1 and value <= 28):
		raise ValidationError(
			_('%(value)s er ikke mellom 1 og 28'),
			params={'value': value},
		)


class FastUtgift(models.Model):
	eier = models.ForeignKey(User, on_delete=models.PROTECT)
	kostnad = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
	dag = models.IntegerField(validators=[validate_lovlig_dato])
	sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
	comment = models.CharField(max_length=100, blank=True)

	def __str__(self):
		return u'%s' % (self.comment)


class Transaction(models.Model):
# A transaction is an action of moving money into and away from accounts
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	account = models.ForeignKey(Account,
		help_text=u'The receiving account',
		on_delete=models.PROTECT)
	amount = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Use negative value if money is to be added to account')
	date = models.DateField(default=datetime.now)
	category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.PROTECT)
	sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
	comment = models.CharField(max_length=100, blank=True)
	is_asset = models.BooleanField(default=False,
		help_text=u'If you want to show this item on the summary page')

	def __str__(self):
		return u'%s: %s' % (self.sub_category, self.amount)

	def completed(self):
		if datetime.date(datetime.now()) >= self.date:
			return True
		return False

	def positive(self):
		if self.amount >= 0:
			return True
		return False

	def balance(self):
		balance = Transaction.objects.filter(
			owner=self.owner,
			account=self.account,
			date__lte=self.date,
		).aggregate(sum=Sum('amount'))['sum']
		return balance

	# REDEFINE SAVE TO UPDATE category


class Salary(models.Model):
# When a salary is added/changed/deleted in this model, the Transactions table must also be updated
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	account = models.ForeignKey(Account,
		help_text=u'The receiving account', on_delete=models.PROTECT)
	date = models.DateField(default=datetime.now)
	salary = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Usually a positive number')
	extra_hours = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Usually a positive number')
	tax = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Usually a negative number')
	retirement_pension = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Usually a negative number')
	labor_union = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Usually a negative number')
	transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT)
	comment = models.CharField(max_length=100, blank=True)

	def __str__(self):
		return u'Lønn: %s på %s' % (self.salary, self.account)

	def amount(self):
		return self.salary + self.extra_hours + self.tax + self.retirement_pension + self.labor_union


class Downpayment(models.Model):
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	date = models.DateField(default=datetime.now)
	interest_and_fees = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
	repayment = models.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Interest and fees pluss repayment will be drawn from the source account')
	source_account = models.ForeignKey(Account, related_name='downpayment_source_account', on_delete=models.PROTECT)
	source_transaction = models.ForeignKey(Transaction, related_name='downpayment_source_transaction', on_delete=models.PROTECT)
	destination_account = models.ForeignKey(Account, related_name='downpayment_destination_account',
		help_text=u'The loan being downpayed', on_delete=models.PROTECT)
	destination_transaction = models.ForeignKey(Transaction, related_name='downpayment_destination_transaction', on_delete=models.PROTECT)
	comment = models.CharField(max_length=100, blank=True,
		help_text=u'Regular payment or extra payment')

	def __str__(self):
		return u'Downpayment %s' % (self.repayment)


class ExpenceForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Transaction
		exclude = ('owner', 'category',)


class SalaryForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Salary
		exclude = ('owner', 'transaction',)


class DownpaymentForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Downpayment
		exclude = ('owner', 'source_transaction', 'destination_transaction')


class TransactionForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(TransactionForm, self).__init__(*args, **kwargs)
		self.fields['source_account'] = forms.ModelChoiceField(queryset=Account.objects.filter(owner=self.user))
		self.fields['destination_account'] = forms.ModelChoiceField(queryset=Account.objects.exclude(account_type=2).filter(owner=self.user))

	def clean_destination_account(self):
		source_account = self.cleaned_data['source_account']
		destination_account = self.cleaned_data['destination_account']
		if source_account == destination_account:
			raise forms.ValidationError("Why transfer from and to the same account?")

		return destination_account

	date = forms.DateField(initial=datetime.now)
	amount = forms.DecimalField(max_digits=MONEY_MAX_DIGITS, decimal_places=MONEY_DECIMAL_PLACES)
	date.widget.format = '%Y-%m-%d'
	date.widget.attrs.update({'class': 'datepicker'})
