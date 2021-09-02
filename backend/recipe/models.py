from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):

    name = models.CharField(max_length=55, verbose_name='Название')
    color = models.CharField('Цвет', max_length=55)
    slug = models.SlugField('Slug', max_length=55, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты',
        through='IngredientRecord',
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Тег')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах', default=1)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

    def validate_cooking_time(self):
        if self.cooking_time < 0:
            raise ValidationError('Время не может быть отрицательное')
        return self.cooking_time


class Follow(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='is_subscribed')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow')
        ]

    def __str__(self) -> str:
        return f'"{self.user} "подписан "{self.author}"'


class ShopList(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепты'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупак'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_shopping_list')
        ]

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.recipe}'


class Favorite(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепты'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.recipe}'


class IngredientRecord(models.Model):

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.FloatField("Значение", null=True)

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'], name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'

    def __unicode__(self):
        return f'?{self.recipe}: {self.ingredient} - {self.amount}'
