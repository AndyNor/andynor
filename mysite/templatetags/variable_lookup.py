from django import template
register = template.Library()

@register.filter
def variable_lookup(mapping, key):
	# Manglende kontekst gir tom streng i maler; unngå TypeError ved ''[key].
	if not isinstance(mapping, dict):
		return None
	try:
		return mapping[key]
	except (KeyError, TypeError):
		return None