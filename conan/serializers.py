from rest_framework import serializers

from .models import *

class ItemSerializer(serializers.ModelSerializer):
	#has_recipe = serializers.ReadOnlyField()
	#itemprice = serializers.ReadOnlyField()
	#parts = serializers.ReadOnlyField()
	#breakdown = serializers.ReadOnlyField()
	#calculated_price = serializers.ReadOnlyField()

	class Meta:
		model = Item
		fields = ('id', 'name', 'stack_price_silver', 'stacksize', 'itemtype', 'properties') #'has_recipe', 'itemprice', 'calculated_price', 'parts', 'breakdown')


class RecipeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Recipe
		fields = ('id', 'item', 'output_factor', 'recipe_comment')


class RecipePartSerializer(serializers.ModelSerializer):
	class Meta:
		model = RecipePart
		fields = ('id', 'recipe', 'item', 'amount')

class ItemTypeChoiceSerializer(serializers.ModelSerializer):
	class Meta:
		model = ItemTypeChoice
		fields = ('id', 'name', 'important')

class OrderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Order
		fields = ('id', 'recipe_comment', 'payout_silver')


class OrderPartSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderPart
		fields = ('id', 'order', 'item', 'amount')


