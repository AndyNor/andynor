from django import template
register = template.Library()

'''
Accepts a request.path and returnes an html bootstrap breadcrumb
'''
HOME_TEXT = 'Home'


class BreadcrumbsNode(template.Node):
	def __init__(self, url):
		self.url = template.Variable(url)

	def render(self, context):
		try:
			url_string = self.url.resolve(context)
			breadcrumb = '<ul class="breadcrumb" style="background-color: transparent; margin-bottom: 0; padding-left: 0">'
			breadcrumb += '<li><a href="/">' + HOME_TEXT + '</a></li>'
			build_url = '/'
			# Not the first, the next to last is the active one and the last '/'' is not interesting
			for part in url_string.split("/")[1:-2]:
				build_url += part + '/'
				breadcrumb += '<li><span class="divider">/</span><a href="' + build_url + '">' + part.capitalize() + '</a></li>'
				# Last part of the split
			breadcrumb += '<li><span class="divider">/</span>' + url_string.split("/")[-2].capitalize() + '</li>'
			breadcrumb += '</ul>'
			return breadcrumb
		except template.VariableDoesNotExist:
			return 'error with url'


@register.tag
def breadcrumbs(parser, token):
	try:
		# split_contents() knows not to split quoted strings.
		tag_name, url = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
	return BreadcrumbsNode(url)
