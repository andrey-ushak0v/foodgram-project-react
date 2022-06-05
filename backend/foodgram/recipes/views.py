from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status, viewsets

from .filters import CustomSearchFilter, RecipeFilter
from .mixins import ListRetriveViewSet
from .models import (BestRecipes, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingList, Tag)
from .serializers import (BestRecipesSerializer, IngredientListSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          TagSerializer)


class IngredientViewSet(ListRetriveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (CustomSearchFilter, )
    search_fields = ('^name', )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

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

    @action(detail=False, methods=["GET"],
            permission_classes=[IsAuthenticated])
    def download_shopping_list(self, request):
        download_list = {}
        ingredients_in_recipe = IngredientsInRecipe.objects.filter(
            recipe__purchases__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
        for i in ingredients_in_recipe:
            name = i[0]
            download_list[name] = {
                    'measurement_unit': i[1],
                    'amount': i[2]
                }
        pdfmetrics.registerFont(
            TTFont('FreeSans', 'media/fonts/FreeSans.ttf'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('FreeSans', size=24)
        page.drawString(200, 600, "Список ингредиентов.")
        page.showPage()
        page.save()
        return response


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientAmountViewSet(generics.ListAPIView):
    queryset = IngredientsInRecipe.objects.all()
    serializer_class = IngredientListSerializer
