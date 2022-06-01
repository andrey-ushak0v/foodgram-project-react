from dataclasses import field
from django.db.models import F
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.serializers import CustomUserSerializer
from drf_extra_fields.fields import Base64ImageField

from .models import Ingredient, IngredientsInRecipe, Tag, Recipe, BestRecipes, ShoppingList

User = get_user_model()

class IngredientListSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only = True)

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'


class IngtedientsInRecipe(serializers.ModelSerializer):
    id = serializers.IntegerField(source = 'ingredient.id')
    amount = serializers.IntegerField()
    
    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientListSerializer(
        many=True, source='ingredients_amount')
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    name = serializers.CharField(required=False)
    ingredients = IngredientListSerializer(
        many=True, source='ingredients_amount')
    text = serializers.CharField(required=False)
    author = CustomUserSerializer(read_only=True)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if ingredients == []:
            raise serializers.ValidationError('выберите хотя бы 1 ингредиент.')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError('количество не может быть'
                                                  'меньше 1.')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError('время приготовления не может быть нулевым')
        return data

    def create(self, validated_data):
        validated_data.pop('ingredients_amount')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        ingredients_amount = self.get_ingredients_list(
            self.initial_data['ingredients'], recipe)
        recipe.tags.set(tags)
        recipe.ingredients_amount.set(ingredients_amount)
        recipe.save()
        return recipe


    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        ingredients_data = validated_data.pop('ingredients_amount', None)
        tags_data = validated_data.pop('tags', None)
        if tags_data:
            instance.tags.set(tags_data)
        if ingredients_data:
            ing = self.initial_data['ingredients']
            ingredients = self.get_ingredients_list(
                ing,
                instance)
            instance.ingredients_amount.set(ingredients)
        instance.save()
        return instance

    def get_ingredients_list(self, ingredients, recipe_id):
        ingredients_list = []
        ingredients_to_del = IngredientsInRecipe.objects.filter(
            recipe=recipe_id)
        if ingredients_to_del:
            for ing in ingredients_to_del:
                ing.delete()
        for ing in ingredients:
            ingredient_id = ing['id']
            amount = ing['amount']
            ingredient_instance = Ingredient.objects.get(
                id=ingredient_id)
            if (IngredientsInRecipe.objects.
               filter(recipe=recipe_id, ingredient_id=ingredient_id).exists()):
                amount += F('amount')
            ing, updated = IngredientsInRecipe.objects.update_or_create(
                recipe=recipe_id, ingredient=ingredient_instance,
                defaults={'amount': amount})
            ingredients_list.append(ing)
        return ingredients_list
        
    class Meta:
        model = Recipe
        fields = '__all__'

class ShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

class BestRecipesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BestRecipes
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortSerializer(
            instance.recipe, context=context).data

class ShoppingListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortSerializer(
            instance.recipe, context=context).data

 
