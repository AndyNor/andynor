from rest_framework import serializers

from .models import *

class ItemSerializer(serializers.ModelSerializer):
	itemtype_str = serializers.SerializerMethodField('_get_itemtype_str')
	def _get_itemtype_str(self, item):
		return item.itemtype.name if hasattr(item, 'itemtype') else None

	related_recipe = serializers.SerializerMethodField('_get_related_recipe')
	def _get_related_recipe(self, item):
		return [item.recipe.id] if item.has_recipe() else None

	class Meta:
		model = Item
		fields = ('id', 'name', 'stack_price_silver', 'stacksize', 'itemtype', 'itemtype_str', 'properties', 'related_recipe') #'has_recipe', 'itemprice', 'calculated_price', 'parts', 'breakdown')


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
		fields = ('id', 'name', 'important', 'color',)

class OrderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Order
		fields = ('id', 'recipe_comment', 'payout_silver')


class OrderPartSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrderPart
		fields = ('id', 'order', 'item', 'amount')


