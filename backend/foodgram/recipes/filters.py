from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_best_recipes')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_best_recipes(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_list(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(basket__user=self.request.user)
        return queryset


class CustomSearchFilter(SearchFilter):
    search_param = 'name'
