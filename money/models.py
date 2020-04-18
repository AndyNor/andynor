# coding=UTF-8
from django.db import models
from django import forms
from django.contrib.auth.models import User
from mysite.models import make_custom_plugins
from datetime import datetime, timedelta
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

	class Meta:
		verbose_name_plural = "kategorier"
		default_permissions = ('add', 'change', 'delete', 'view')


class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		exclude = ('owner',)

	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		self.fields['text_color'].widget.attrs['class'] = 'color'


class SubCategory(models.Model):
# Sub categories are required. They link back to a generic category
	owner = models.ForeignKey(
		to=User,
		on_delete=models.PROTECT,
	)
	name = models.CharField(
		max_length=25,
	)
	parent_category = models.ForeignKey(
		to=Category,
		related_name='subcategory_parent_category',
		on_delete=models.PROTECT,
	)
	description = models.CharField(
		max_length=200,
		blank=True,
	)

	def __str__(self):
		return u'%s' % (self.name)

	class Meta:
		verbose_name_plural = "Underkategorier"
		default_permissions = ('add', 'change', 'delete', 'view')


class SubCategoryForm(forms.ModelForm):
	class Meta:
		model = SubCategory
		exclude = ('owner',)


class Account(models.Model):
	ACCOUNT_TYPE_CHOISES = (
		(u'0', u'Expence'),  # Expence account from where you pay for goods
		(u'1', u'Saving'),  # Savings account you don't pay directly with. Usually with higher interest
		(u'2', u'Loan'),  # Loan accounts. Mortgage loans like car and house
	)
	owner = models.ForeignKey(
		to=User,
		on_delete=models.PROTECT,
		)
	name = models.CharField(
		max_length=25,
		)
	account_type = models.CharField(
		max_length=1,
		choices=ACCOUNT_TYPE_CHOISES,
		)
	sub_category = models.ForeignKey(
		to=SubCategory,
		on_delete=models.PROTECT,
		)
	description = models.CharField(
		max_length=200,
		blank=True,
		)
	account_id = models.CharField(
		max_length=64,
		blank=True,
		)
	account_number = models.CharField(
		max_length=32,
		blank=True,
		)
	available = models.DecimalField(
		max_digits=MONEY_MAX_DIGITS,
		decimal_places=MONEY_DECIMAL_PLACES,
		default=0,
		)
	balance = models.DecimalField(
		max_digits=MONEY_MAX_DIGITS,
		decimal_places=MONEY_DECIMAL_PLACES,
		default=0,
		)
	credit_limit = models.DecimalField(
		max_digits=MONEY_MAX_DIGITS,
		decimal_places=MONEY_DECIMAL_PLACES,
		default=0,
		)

	def __str__(self):
		return u'%s' % (self.name)

	class Meta:
		verbose_name_plural = "Kontoer"
		default_permissions = ('add', 'change', 'delete', 'view')

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

	class Meta:
		verbose_name_plural = "Faste utgifter"
		default_permissions = ('add', 'change', 'delete', 'view')


class Transaction(models.Model):
# A transaction is an action of moving money into and away from accounts
	owner = models.ForeignKey(
		to=User,
		on_delete=models.PROTECT,
	)
	account = models.ForeignKey(
		to=Account,
		help_text=u'The receiving account',
		on_delete=models.PROTECT,
	)
	amount = models.DecimalField(
		max_digits=MONEY_MAX_DIGITS,
		decimal_places=MONEY_DECIMAL_PLACES,
		help_text=u'Use negative value if money is to be added to account',
	)
	date = models.DateField(
		default=datetime.now,
	)
	category = models.ForeignKey(
		to=Category,
		blank=True, null=True,
		on_delete=models.PROTECT,
	)
	sub_category = models.ForeignKey(
		to=SubCategory,
		on_delete=models.PROTECT,
	)
	comment = models.CharField(
		max_length=100,
		blank=True,
	)
	is_asset = models.BooleanField(
		default=False,
		help_text=u'If you want to show this item on the summary page',
	)

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

	class Meta:
		verbose_name_plural = "Transaksjoner"
		default_permissions = ('add', 'change', 'delete', 'view')
		ordering = ['-date']

class TransactionForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(TransactionForm, self).__init__(*args, **kwargs)
		self.fields['source_account'] = forms.ModelChoiceField(queryset=Account.objects.filter(owner=self.user))
		self.fields['destination_account'] = forms.ModelChoiceField(queryset=Account.objects.exclude(account_type=2))

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



class BankTransaction(models.Model):
	eier = models.ForeignKey(
		to=User,
		on_delete=models.PROTECT,
		blank=False, null=False,
		verbose_name="Eier",
		help_text=u"",
		)
	account = models.ForeignKey(
		to=Account,
		on_delete=models.PROTECT,
		blank=False, null=False,
		verbose_name="Konto",
		help_text=u"",
		)
	accounting_date = models.DateField(
		blank=False, null=False,
		verbose_name="Transaksjonsdato",
		help_text=u"",
		)
	amount = models.DecimalField(
		max_digits=MONEY_MAX_DIGITS,
		decimal_places=MONEY_DECIMAL_PLACES,
		blank=False, null=False,
		verbose_name="Beløp",
		help_text=u"",
		)
	description = models.TextField(
		blank=False, null=False,
		verbose_name="Beskrivelse",
		help_text=u"",
		)
	related_transaction = models.OneToOneField(
		to="Transaction",
		on_delete=models.PROTECT,
		blank=True, null=True,
		verbose_name="Tilknyttet transaksjon",
		help_text=u"",
		)
	unique_reference = models.CharField(
		max_length=256,
		blank=False,
		null=False,
		unique=True,
		)

	def __str__(self):
		return u'%s' % (self.accounting_date)

	class Meta:
		verbose_name_plural = "Banktransaksjoner"
		default_permissions = ('add', 'change', 'delete', 'view')

class BankTransactionForm(forms.ModelForm):
	class Meta:
		model = BankTransaction
		exclude = ('eier',)

	def __init__(self, *args, **kwargs):
		super(BankTransactionForm, self).__init__(*args, **kwargs)
		if self.instance:
			end_time = datetime.now()
			start_time = end_time - timedelta(days=10)
			self.fields['unique_reference'].queryset = Transaction.objects.filter(owner=self.instance.eier).filter(owner=self.instance.eier).filter(date__range=(start_time, end_time))


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
		return u'Inntekt %s, skatt %s på konto %s' % (self.salary, self.tax, self.account)

	def amount(self):
		return self.salary + self.extra_hours + self.tax + self.retirement_pension + self.labor_union

	class Meta:
		verbose_name_plural = "Inntekter"
		default_permissions = ('add', 'change', 'delete', 'view')


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

	class Meta:
		verbose_name_plural = "Nedbetalinger"
		default_permissions = ('add', 'change', 'delete', 'view')


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


