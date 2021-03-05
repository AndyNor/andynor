from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from .models import *
from .serializers import *
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse


from mysite.site_wide_functions import set_redirect_session

def index(request):
	set_redirect_session(request, 'app_conan', None)
	items = Item.objects.order_by('itemtype', 'name')
	#parts_cache = Item.parts.cache_info()
	#breakdown_cache = Item.breakdown.cache_info()
	#calculated_price_cache = Item.calculated_price.cache_info()

	return render(request, u'conan.html', {
		'items': items,
		#'parts_cache': parts_cache,
		#'breakdown_cache': breakdown_cache,
		#'calculated_price_cache': calculated_price_cache,
	})


def orders(request):
	set_redirect_session(request, 'orders', None)
	orders = Order.objects.all()

	return render(request, u'orders.html', {
		'orders': orders,
	})


#def orders(request):
#	orders = Order.objects.all()
#	return render(request, u'conan_orders.html', {
#		'orders': orders,
#	})


def item_details(request, pk):
	set_redirect_session(request, 'item_details', {'pk': pk})
	item = Item.objects.get(pk=pk)
	return render(request, u'conan_details.html', {
		'item': item,
	})


class MyDjangoJSONEncoder(DjangoJSONEncoder):
	def default(self, o):
		if isinstance(o, Decimal):
			return float(o)
		return super().default(o)


def all_items(request):
	data = []
	all_items = Item.objects.all()
	for item in all_items:
		data.append({
			"item_id": item.pk,
			"item_type": item.itemtype.name,
			"item_name": item.name,
			"item_unit_price": item.calculated_price(),
			"item_stacksize": item.stacksize,
			"item_stackcost": item.calculated_price() * item.stacksize,
			})
	return JsonResponse(encoder=MyDjangoJSONEncoder, data=data, safe=False)


def order_details_api(request, pk):
	order = Order.objects.get(pk=pk)
	order_items = [
				{
				"item_id": order_part.item.pk,
				"item_type": order_part.item.itemtype.name,
				"item_name": order_part.item.name,
				"amount_wanted": order_part.amount,
				"item_cost_silver": order_part.item.calculated_price(),
				"total_cost_silver": order_part.amount * order_part.item.calculated_price(),
				} for order_part in order.parts.all()
			]

	data = {
		"order_id": order.pk,
		"order_recipe_comment": order.recipe_comment,
		"order_payout_silver": order.payout_silver,
		"order_material_cost": order.cost(),
		"order_parts": order_items,

		}
	return JsonResponse(encoder=MyDjangoJSONEncoder, data=data, safe=False)


def item_details_api(request, pk):

	def JSONserialize(data):
		serialized_data = []
		for i in data:
			if type(i["item"]) != int:
				item = i["item"]
				i["item"] = item.pk
				i["name"] = item.name
			else:
				instance = Item.objects.get(pk=i["item"])
				i["item"] = instance.pk
				i["name"] = instance.name

			i["price"] = i['price']
			i["amount"] = i['amount']
			serialized_data.append(i)
		return serialized_data

	item = Item.objects.get(pk=pk)
	item_breakdown = JSONserialize(item.breakdown()) if item.breakdown() != [] else None
	item_recipe = JSONserialize(item.parts()) if item.parts() != [] else None
	usedin = [{"item": recipepart.recipe.item.pk, "item_name": recipepart.recipe.item.name} for recipepart in item.usedin()]

	data = {
		"item_id": item.pk,
		"item_type": item.itemtype.name,
		"item_name": item.name,
		"item_calculated_price": float(item.calculated_price()),
		"item_recipe": item_recipe,
		"item_recipe_output": item.recipe_output_factor(),
		"item_breakdown": item_breakdown,
		"used_in": usedin,
		}
	return JsonResponse(encoder=MyDjangoJSONEncoder, data=data, safe=False)

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

class ItemTypeChoiceViewSet(viewsets.ModelViewSet):
	queryset = ItemTypeChoice.objects.all()
	serializer_class = ItemTypeChoiceSerializer

class OrderSerializerViewSet(viewsets.ModelViewSet):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer


class OrderPartSerializerViewSet(viewsets.ModelViewSet):
	queryset = OrderPart.objects.all()
	serializer_class = OrderPartSerializer

