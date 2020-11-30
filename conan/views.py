from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from conan.models import *

from mysite.site_wide_functions import get_previous_page, set_redirect_session

# This function really only wants to figyre out what one stack of the items would cost in silver, based on all underlying recipes.
# TODO: It is possible to model loops. Loop protection (hard limit or detection) is not implemented yet.
def determine_price(item):
	print("\nlookup of price for %s" % (item))
	recipes = item.all_recipes.all()
	for recipe in recipes:
		items_needed = []
		result = []
		for part in recipe.all_recipe_parts.all():
			print("%s: %s %s" % (recipe, part.amount, part.item))
			items_needed.append({"item": part.item, "amount": part.amount})

		while items_needed:
			current_part = items_needed.pop()
			required_amount = current_part["amount"]
			item_part = current_part["item"]
			all_recipes = item_part.all_recipes.all()
			if len(all_recipes) == 0:
				part_price = item_part.itemprice() * required_amount
				result.append({"item": item_part, "amount": required_amount, "price": part_price})
			else:
				# there might be more, we only support one at the moment, hence [0] first item
				for part in all_recipes[0].all_recipe_parts.all():
					adjusted_amount = required_amount * part.amount
					print("%s: %s %s" % (item_part, adjusted_amount, part.item))
					items_needed.append({"item": part.item, "amount": adjusted_amount})

		total_cost_recipe = 0
		for r in result:
			total_cost_recipe += r["price"]

		calculated_stackprice = total_cost_recipe * item.stacksize

		return {"calculated_stackprice": calculated_stackprice, "result": result,}
	return {"calculated_stackprice": None, "result": None,} # default


def index(request):
	items = Item.objects.all().order_by('-itemtype')
	for item in items:
		if item.price == 0:
			item.price = determine_price(item)["calculated_stackprice"]

	return render(request, u'conan.html', {
		'items': items,
	})


def item_details(request, pk):
	set_redirect_session(request, 'item_details', {'pk': pk})
	item = Item.objects.get(pk=pk)
	calculations = determine_price(item)
	if item.price == 0:
		item.price = calculations["calculated_stackprice"]

	return render(request, u'conan_details.html', {
		'item': item, # converting to a set in order to make it iterable for the template
		'calculation': calculations["result"],
	})
