from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Ingredient, IngredientsInRecipe, Recipe, Tag, BestRecipes, ShoppingList
from .mixins import ListRetriveViewSet
from .serializers import IngredientListSerializer, IngredientSerializer, RecipeCreateSerializer, RecipeSerializer, TagSerializer, BestRecipesSerializer, ShoppingListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class IngredientViewSet(ListRetriveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    #serializer_class = RecipeSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def best_recipes(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=BestRecipesSerializer
        )

    @best_recipes.mapping.delete
    def delete_best_recipes(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=BestRecipes
        )

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_list(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingListSerializer
        )

    @shopping_list.mapping.delete
    def delete_shopping_list(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingList
        )

    
class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientAmountViewSet(generics.ListAPIView):
    queryset = IngredientsInRecipe.objects.all()
    serializer_class = IngredientListSerializer
