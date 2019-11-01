from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def percent(value, delimiter=None):
	value = round(float(value.split(delimiter)[0]), 3)
	return "%s%%" % (value * 100)
percent.is_safe = True
