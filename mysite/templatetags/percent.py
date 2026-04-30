from django import template
from django.template.defaultfilters import stringfilter
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

register = template.Library()


@register.filter
@stringfilter
def percent(value, delimiter=None):
	try:
		raw = value.split(delimiter)[0] if delimiter else value
		raw = raw.strip().replace(' ', '').replace(',', '.')
		pct = (Decimal(raw) * Decimal('100')).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
		s = format(pct, 'f').rstrip('0').rstrip('.')
		return f"{s}%"
	except (InvalidOperation, ValueError, TypeError):
		return ""
percent.is_safe = True
