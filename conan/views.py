from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import *
from .serializers import *


from mysite.site_wide_functions import set_redirect_session

def index(request):
	important_items = Item.objects.filter(itemtype__important=True).order_by('name')
	lesser_items = Item.objects.filter(itemtype__important=False).order_by('name')
	return render(request, u'conan.html', {
		'important_items': important_items,
		'lesser_items': lesser_items,
	})

def item_details(request, pk):
	set_redirect_session(request, 'item_details', {'pk': pk})
	item = Item.objects.get(pk=pk)
	return render(request, u'conan_details.html', {
		'item': item, # converting to a set in order to make it iterable for the template
	})

def item_details_api(request, pk):
	from django.http import JsonResponse

	def JSONserialize(data):
		serialized_data = []
		for i in data:
			item = i["item"]
			i["item"] = item.pk
			i["name"] = item.name
			serialized_data.append(i)
		return serialized_data

	item = Item.objects.get(pk=pk)
	item_breakdown = JSONserialize(item.breakdown()) if item.breakdown() != [] else None
	item_recipe = JSONserialize(item.parts()) if item.parts() != [] else None

	data = {
		"item_id": item.pk,
		"item_name": item.name,
		"item_calculated_price": item.calculated_price(),
		"item_recipe": item_recipe,
		"item_recipe_output": item.recipe_output_factor(),
		"item_breakdown": item_breakdown,
		}
	return JsonResponse(data, safe=False)

class ItemViewSet(viewsets.ModelViewSet):
	queryset = Item.objects.all().order_by('name')
	serializer_class = ItemSerializer
	"""
	detail_serializer_class = ItemDetailSerializer

	def get_serializer_class(self):
		if self.action == 'retrieve':
			if hasattr(self, 'detail_serializer_class'):
				return self.detail_serializer_class

		return super(ItemViewSet, self).get_serializer_class()
	"""

class RecipeViewSet(viewsets.ModelViewSet):
	queryset = Recipe.objects.all()
	serializer_class = RecipeSerializer

class RecipePartViewSet(viewsets.ModelViewSet):
	queryset = RecipePart.objects.all()
	serializer_class = RecipePartSerializer

