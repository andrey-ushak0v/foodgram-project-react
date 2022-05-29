from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Ingredient, IngredientsInRecipe, Recipe, Tag
from .mixins import ListRetriveViewSet
from .serializers import IngredientListSerializer, IngredientSerializer, RecipeCreateSerializer, RecipeSerializer, TagSerializer
from django_filters.rest_framework import DjangoFilterBackend


class IngredientViewSet(ListRetriveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    #serializer_class = RecipeSerializer
    
    def get_serializer_class(self):
        if self.action in ['creste', 'partial_update']:
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



class TagViewSet(ListRetriveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientAmountViewSet(generics.ListAPIView):
    queryset = IngredientsInRecipe.objects.all()
    serializer_class = IngredientListSerializer
