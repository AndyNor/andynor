from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'item', views.ItemViewSet)
router.register(r'recipe', views.RecipeViewSet)
router.register(r'recipepart', views.RecipePartViewSet)
router.register(r'itemtypechoice', views.ItemTypeChoiceViewSet)
router.register(r'order', views.OrderSerializerViewSet)
router.register(r'orderpart', views.OrderPartSerializerViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]