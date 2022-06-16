from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    best_recipes = filters.BooleanFilter(method='filter_best_recipes')
    shopping_list = filters.BooleanFilter(
        method='filter_shopping_list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'best_recipes', 'shopping_list')

    def filter_best_recipes(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_list(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(purchases__user=self.request.user)
        return queryset


class CustomSearchFilter(SearchFilter):
    search_param = 'name'
