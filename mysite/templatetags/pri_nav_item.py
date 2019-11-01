from django import template
import re
register = template.Library()

'''
outputs elements used in bootstrap main menu
'''


class PriNavItemNode(template.Node):
	def __init__(self, active_url, url, name, icon):
		self.active_url = template.Variable(active_url)
		self.url = template.Variable(url)
		self.name = template.Variable(name)
		self.icon = template.Variable(icon)

	def render(self, context):
		try:
			active_url = self.active_url.resolve(context)
			url = self.url.resolve(context)
			name = self.name.resolve(context)
			icon = self.icon.resolve(context)
			#print 'active url %s - %s' % (active_url, url)
			if re.search(url, active_url) != None:
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
		tag_name, active_url, url, name, icon = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
	return PriNavItemNode(active_url, url, name, icon)
