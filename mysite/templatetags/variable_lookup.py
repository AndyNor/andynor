from django import template
register = template.Library()

@register.filter
def variable_lookup(dict, key):
	try:
		return dict[key]
	except:
		return None