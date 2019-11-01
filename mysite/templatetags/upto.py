from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


# http://stackoverflow.com/questions/6481788/format-of-timesince-filter
@register.filter
@stringfilter
def upto(value, delimiter=None):
	return value.split(delimiter)[0]
upto.is_safe = True


@register.filter
@stringfilter
def goback(value, delimiter=None):
	return value.split(delimiter)[0]
goback.is_safe = True


@register.filter
@stringfilter
def mintohour(value, delimiter=None):
	minutes = int(value.split(delimiter)[0])
	if minutes is not 0:
		return "%s:%s" % (minutes // 60, minutes % 60)
	else:
		return ""
mintohour.is_safe = True
