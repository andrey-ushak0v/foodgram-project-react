from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.settings import FILE_NAME
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

    @action(detail=True, methods=['POST'],
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

    @action(detail=True, methods=['POST'],
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

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_list(self, request):
        download_list = {}
        ingredients_in_recipe = IngredientsInRecipe.objects.filter(
            recipe__basket__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
        for i in ingredients_in_recipe:
            name = i[0]
            if name not in download_list:
                download_list[name] = {
                        'measurement_unit': i[1],
                        'amount': i[2]
                    }
            else:
                download_list[name]['amount'] += i[2]
        pdfmetrics.registerFont(
            TTFont('DejaVuSans', 'media/fonts/DejaVuSans.ttf'))
        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = (
            f'attachment; filename = {FILE_NAME}')
        page = canvas.Canvas(response)
        page.setFont('DejaVuSans', size=24)
        page.drawString(200, 600, 'Список ингредиентов')
        page.setFont('DejaVuSans', size=16)
        height = 750
        for i, (name, data) in enumerate(download_list.items(), start=1):
            page.drawString(75, height, (f'{i}) {name} - {data["amount"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response

    def get_permissions(self):
        if self.action in ['shopping_list', 'download_shopping_list']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [Author | ReadOnly]
        return [permission() for permission in permission_classes]


class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientAmountViewSet(generics.ListAPIView):
    queryset = IngredientsInRecipe.objects.all()
    serializer_class = IngredientListSerializer
