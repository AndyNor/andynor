from django.db import models

MAX_DIGITS = 10
DECIMAL_PLACES = 4

# Here we are trying to model how materials in Conan Exiles are converted to items via recipes.
# The "Item"-class is any item. Basic resource or a final product. Typically a resource must go through several transformations in order to become a useful final product.
# The "Recipe"-class is used to represent a transformation. In some cases there are multiple recipes for crafting an item. In order to be able to calculate a price in such caes, we could either calculate all possible prices/combinations of how to make an item, or we can simply limit the modelling a preferred way/only allow one recipe for simplification.
# The "recipe" can have a output factor. A factor of 1 is normal. You get one end result for every instance of the recipe. It can however be much larger. One example is the legendary weapon repair kit witch gives 5 kits.
# A recipe can in some rare cases have more than one output. Such an example is how hide is converted to leather and tar. This is very uncomon and would increase the complexity of the model significantly. Thus we simply ignore this detail and seperate out the recipes. One for tar and one for hide, although they both consume the same hide.
# The "RecipePart"-class is used to modell what items and the number of such item is needed in the recipe.

# An items has a stack size and a price. The stack size is simply how many items are treated as one movable unit in Conan Exiles. Price is in silver for a complete stack. If price is 0, then we assume we must traverse the dependencies in order to calculate the price. If price is given, we can use that value directly.

# Usage: Register items. Items that are not harvested directly in the world (except from drops from NPC's and chests) need a corresponding recipe. Then add recipe parts as needed.


class ItemTypeChoice(models.Model):
	name = models.CharField(
		max_length=200,
		verbose_name="Item type choice",
		)
	def __str__(self):
		return u'%s' % (self.name)

	class Meta:
		verbose_name_plural = "Item type choices"
		default_permissions = ('add', 'change', 'delete', 'view')


class Item(models.Model):
	name = models.CharField(
		max_length=200,
		verbose_name="Name of resource or item",
		)
	itemtype = models.ForeignKey(
		to=ItemTypeChoice,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		)
	price = models.DecimalField(
		max_digits=MAX_DIGITS,
		decimal_places=DECIMAL_PLACES,
		default=0,
		verbose_name="Price in silver per stack",
		)
	stacksize = models.IntegerField(
		default=1,
		blank=False, null=False,
		verbose_name="Stack size",
		)

	def has_recipe(self):
		return False if len(self.all_recipes.all()) == 0 else True

	def number_of_recipes(self):
		return len(self.all_recipes.all())

	def itemprice(self):
		try:
			return (self.price / self.stacksize)
		except:
			return "Not a number"

	def __str__(self):
		return u'%s' % (self.name)

	class Meta:
		verbose_name_plural = "Items"
		default_permissions = ('add', 'change', 'delete', 'view')

class Recipe(models.Model):
	item = models.ForeignKey(
		to=Item,
		related_name='all_recipes',
		on_delete=models.CASCADE,
		)
	output_factor = models.IntegerField(
		default=1,
		blank=False, null=False,
		verbose_name='Output factor',
		)
	recipe_comment = models.CharField(
		max_length=50,
		verbose_name="Item type choice",
		blank=True, null=True,
		)

	def __str__(self):
		return u'%s %s' % (self.item, self.recipe_comment) if self.recipe_comment else u'%s' % (self.item)

	class Meta:
		verbose_name_plural = "Recipes"
		default_permissions = ('add', 'change', 'delete', 'view')


class RecipePart(models.Model):
	recipe = models.ForeignKey(
		to=Recipe,
		related_name='all_recipe_parts',
		on_delete=models.CASCADE,
	)
	item = models.ForeignKey(
		to=Item,
		on_delete=models.SET_NULL,
		null=True,
		blank=False,
	)
	amount = models.IntegerField(
		default=1,
		blank=False, null=False,
	)


	def __str__(self):
		return u'%s' % (self.item)

	class Meta:
		verbose_name_plural = "Recipe Parts"
		default_permissions = ('add', 'change', 'delete', 'view')