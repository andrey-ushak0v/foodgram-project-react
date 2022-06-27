from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import FILE_NAME
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.filters import CustomSearchFilter, RecipeFilter
from recipes.mixins import ListRetriveViewSet
from recipes.models import (BestRecipes, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingList, Tag)
from recipes.permissions import Author, ReadOnly
from recipes.serializers import (BestRecipesSerializer,
                                 IngredientListSerializer,
                                 IngredientSerializer, RecipeCreateSerializer,
                                 RecipeSerializer, ShoppingListSerializer,
                                 TagSerializer)

CONTENT_TYPE = 'application/pdf'


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
        if self.action in ('create', 'partial_update',):
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

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=BestRecipesSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=BestRecipes
        )

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingListSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingList
        )

    @action(detail=False, methods=('GET',),
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients_in_recipe = IngredientsInRecipe.objects.filter(
            recipe__basket__user=request.user).values_list(
                'ingredient__name', 'ingredient__measurement_unit',
        ).order_by(
                'ingredient__name').annotate(Sum('amount'))
        pdfmetrics.registerFont(
            TTFont('DejaVuSans', 'media/fonts/DejaVuSans.ttf'))
        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename = {FILE_NAME}')
        page = canvas.Canvas(response)
        page.setFont('DejaVuSans', size=24)
        page.drawString(50, 100, 'Список ингредиентов')
        page.setFont('DejaVuSans', size=16)
        height = 750
        for i, item in enumerate(ingredients_in_recipe, start=1):
            page.drawString(75,
                            height,
                            (f'{i}. {item[0]} '
                             f' {item[2]}'
                             f' {item[1]}.'))
            height -= 25
        page.showPage()
        page.save()
        return response

    def get_permissions(self):
        if self.action in ('shopping_cart', 'download_shopping_cart',):
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (Author | ReadOnly,)
        return tuple([permission() for permission in permission_classes])


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientAmountViewSet(generics.ListAPIView):
    queryset = IngredientsInRecipe.objects.all()
    serializer_class = IngredientListSerializer
