from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=30,
        unique=True
        )
    color = models.CharField(
        verbose_name='цветовой код',
        max_length=10,
        unique=True,
        null=True
        )
    slug = models.SlugField(
        verbose_name='слаг',
        max_length=90,
        unique=True,
        null=True
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='название ингридиента',
        max_length=100
        )
    measurement_unit = models.CharField(
        verbose_name='единицы измерения',
        max_length=30
        )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(verbose_name='названме рецепта', max_length=100)
    author = models.ForeignKey(User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
        )
    image = models.ImageField(
        verbose_name='картинка'
        )
    text = models.TextField(
        max_length=500,
        verbose_name='описание рецепта',
        help_text='введите описание рецепта'
        )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe'
        )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='tags'
        )
    cook_time = models.PositiveIntegerField(
        verbose_name='время приготовления',
        validators=[MinValueValidator (1, 
        'слишком малое значение')]
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='ingredients_amount'
        ) 
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amount'
        )
    amount = models.PositiveIntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1,
        'слишком малое значение')]
        )
        
    class Meta:
        verbose_name = 'кол-во ингридиентов в рецепте'
        verbose_name_plural = 'кол-во ингридиентов в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'], name='unique_recipe')
        ]


class BestRecipes(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='favorites'
        )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='favorites',
        null=True,
        blank=True
        )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
                models.UniqueConstraint(
                    fields=['user', 'recipe'], name='unique_recipe')
            ]

    def __str__(self):
        return f'пользователь {self.user} добавил в избранное {self.recipe}'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
        related_name='basket'
        )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт',
        related_name='basket'
        )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = [
                models.UniqueConstraint(
                    fields=['user', 'recipe'], name='unique_basket')
            ]
    


