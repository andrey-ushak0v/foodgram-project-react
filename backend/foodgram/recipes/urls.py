
from rest_framework.routers import DefaultRouter
from django.urls import include, path

from recipes.views import IngredientViewSet, RecipeViewSet

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipe')


urlpatterns = [
    path('', include(router.urls)),
]