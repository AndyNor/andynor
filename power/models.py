# coding=UTF-8
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  # create own validation rules
from mysite.models import make_custom_plugins
import datetime


KWH_MAX_LENGTH = 12
POWER_MAX_DIGITS = 15
POWER_DECIMAL_PLACES = 4


def validate_kwh(value):
	if value < 0:
		raise ValidationError('Negative numbers are not allowed')


def validate_date(value):
	today = datetime.date.today()
	if value > today:
		raise ValidationError('You can not register a reading into the future')


class Payment(models.Model):
	owner = models.ForeignKey(User, on_delete=models.PROTECT)
	date = models.DateField()
	kwh_usage = models.IntegerField()
	kwh_usage_cost = models.DecimalField(max_digits=POWER_MAX_DIGITS, decimal_places=POWER_DECIMAL_PLACES)
	kwh_rent_cost = models.DecimalField(max_digits=POWER_MAX_DIGITS, decimal_places=POWER_DECIMAL_PLACES)
	fixed_cost = models.DecimalField(max_digits=POWER_MAX_DIGITS, decimal_places=POWER_DECIMAL_PLACES)

	def __str__(self):
		return u'%s' % (self.kwh_usage)

	''' In Norway we usually pay a variable price per kwh used
	+ a fixed price per kwh ('nettleie'). In addition one might
	have a fixed price independent of usage'''

	def cost_usage(self):
		return self.kwh_usage * self.kwh_usage_cost

	def cost_rent(self):
		return self.kwh_usage * self.kwh_rent_cost

	def cost_total(self):
		return self.cost_usage() + self.cost_rent() + self.fixed_cost


class PaymentForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = Payment
		exclude = ('owner',)
