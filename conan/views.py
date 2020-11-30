from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from conan.models import *

from mysite.site_wide_functions import set_redirect_session

def index(request):
	items = Item.objects.all().order_by('-itemtype')
	return render(request, u'conan.html', {
		'items': items,
	})

def item_details(request, pk):
	set_redirect_session(request, 'item_details', {'pk': pk})
	item = Item.objects.get(pk=pk)
	return render(request, u'conan_details.html', {
		'item': item, # converting to a set in order to make it iterable for the template
	})
