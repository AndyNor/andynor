# coding=UTF-8
from django.contrib.syndication.views import Feed
from blog.models import Blog


class LatestEntriesFeed(Feed):
	description_template = 'feeds/descriptions.html'
	title = "André Nordbø's RSS"
	link = "/blog/"  # this is the "magic"
	description = "Det siste fra andynor.net"

	def items(self):
		return Blog.objects.filter(published=True).order_by('-created')[:10]

	def item_title(self, item):
		return item.title

	def item_pubdate(self, item):
		return item.created

	def item_description(self, item):
		return item.content
