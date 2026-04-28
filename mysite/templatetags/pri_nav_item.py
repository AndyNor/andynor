from django import template
import re
register = template.Library()

'''
outputs elements used in bootstrap main menu
'''


class PriNavItemNode(template.Node):
	def __init__(self, active_url, url, name, icon, suppress_active=False):
		self.active_url = template.Variable(active_url)
		self.url = template.Variable(url)
		self.name = template.Variable(name)
		self.icon = template.Variable(icon)
		self.suppress_active = template.Variable(suppress_active) if suppress_active else None

	def render(self, context):
		try:
			active_url = self.active_url.resolve(context)
			url = self.url.resolve(context)
			name = self.name.resolve(context)
			icon = self.icon.resolve(context)
			suppress_active = False
			if self.suppress_active is not None:
				suppress_active = bool(self.suppress_active.resolve(context))
			#print 'active url %s - %s' % (active_url, url)
			if (not suppress_active) and re.search(url, active_url) != None:
				class_string = 'active'
			else:
				class_string = ''
			return '<li class="%s"><a href="%s"><i class="%s"></i> %s</a></li>' % (class_string, url, icon, name)
		except template.VariableDoesNotExist:
			return 'error with the url'


@register.tag
def pri_nav_item(parser, token):
	try:
		# split_contents() knows not to split quoted strings.
		parts = token.split_contents()
		tag_name = parts[0]
		if len(parts) == 5:
			_, active_url, url, name, icon = parts
			suppress_active = False
		elif len(parts) == 6:
			_, active_url, url, name, icon, suppress_active = parts
		else:
			raise ValueError
	except ValueError:
		raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
	return PriNavItemNode(active_url, url, name, icon, suppress_active)
