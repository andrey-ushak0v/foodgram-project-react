
from rest_framework.routers import DefaultRouter
from django.urls import include, path

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipe')
router.register('tags', TagViewSet, 'tag')


urlpatterns = [
    path('', include(router.urls)),
]