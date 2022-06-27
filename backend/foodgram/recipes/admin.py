from django.contrib import admin

from recipes.models import (BestRecipes, Ingredient, IngredientsInRecipe,
                            Recipe, ShoppingList, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    fields = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('measurement_unit', 'name',)
    list_filter = ('measurement_unit',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientsInRecipe


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientRecipeInline,
    ]
    list_display = ('id', 'name', 'author', 'get_ingredients')
    list_filter = ('tags',)
    search_fields = ('name', 'author__username', 'author__email',)

    def get_ingredients(self, obj):
        return '\n'.join(
            [str(ingredients) for ingredients in obj.ingredients.all()])


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    fields = ('ingredient', 'recipe', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)


class BestRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = (
        'user__username', 'user__email', 'recipe__name',)


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(BestRecipes, BestRecipesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
