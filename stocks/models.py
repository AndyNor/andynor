# coding=UTF-8
from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db import models
from datetime import date
from django import forms
from mysite.models import make_custom_plugins

# Create your models here.

def validate_positive_number(value):
	if value < 0:
		raise ValidationError('Negative numbers are not allowed')

def validate_not_future(value):
	today = date.today()
	if value > today:
		raise ValidationError('You can not register a transaction into the future')


class Ticker(models.Model):
	company_name = models.CharField(max_length=30)
	ticker_name = models.CharField(max_length=6)
	def __str__(self):
		return u'%s' % (self.company_name)

class TickerForm(forms.ModelForm):
	class Meta:
		model = Ticker
		fields = ('company_name', 'ticker_name')

class Transaction(models.Model):
	ticker = models.ForeignKey('Ticker', on_delete=models.CASCADE)
	date = models.DateField(validators=[validate_not_future])
	amount = models.IntegerField(help_text=u'Antall aksjer. Negativt hvis salg.')
	total_price = models.DecimalField(max_digits=18, decimal_places=3, help_text=u'Kjøpesum inkludert kurtasje. Negativt hvis salg.')
	brokerage = models.DecimalField(max_digits=18, decimal_places=3, validators=[validate_positive_number])
	def __str__(self):
		if self.amount < 0:
			message = u"solgte %s aksjer" % (-self.amount)  #  sold # stocks
		else:
			message = u"kjøpte %s aksjer" % (self.amount)  # bought # stocks
		return u'%s: %s' % (self.ticker, message)


class TransactionForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Transaction
		fields = ('ticker', 'date', 'amount', 'total_price', 'brokerage')


class TickerHistory(models.Model):
	ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
	date = models.DateField(validators=[validate_not_future])
	price = models.DecimalField(max_digits=9, decimal_places=3, validators=[validate_positive_number])
	def __str__(self):
		return u'%s - %s' % (self.ticker, self.date)

class TickerHistoryForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = TickerHistory
		fields = ('ticker', 'date', 'price')
