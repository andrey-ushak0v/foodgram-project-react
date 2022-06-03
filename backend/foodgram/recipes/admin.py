from django.contrib import admin

from .models import (BestRecipes, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingList, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    fields = ['name', 'color', 'slug']


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ['name']


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientsInRecipe


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        IngredientRecipeInline,
    ]
    list_display = ('id', 'name', 'author', 'get_ingredients')
    list_filter = ('name', 'author', 'tags')

    def get_ingredients(self, obj):
        return '\n'.join(
            [str(ingredients) for ingredients in obj.ingredients.all()])


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    fields = ['ingredient', 'recipe', 'amount']


class BestRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(BestRecipes, BestRecipesAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
