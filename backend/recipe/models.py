from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


User = get_user_model()


class Recipe(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор', related_name='recipes')
    name = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField('Изображение', upload_to='recipe/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        'Ingredients', related_name='recipes', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        'Tag', related_name='recipes', verbose_name='Тег')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах', default=1)

    def __str__(self) -> str:
        return self.name

    def validate_cooking_time(self):
        if self.cooking_time < 0:
            raise ValidationError('Время не может быть отрицательным')
        return self.cooking_time

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Tag(models.Model):

    name = models.CharField(max_length=55, verbose_name='Название')
    color = models.CharField('Цвет', max_length=55)
    slug = models.SlugField('Slug', max_length=55, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(models.Model):

    name = models.CharField('Название', max_length=155)
    amount = models.PositiveSmallIntegerField('Количество')
    measurement_unit = models.CharField('Еденица измерения', max_length=155)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Follow(models.Model):

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='is_subscribed')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'"{self.user} "подписан "{self.author}"'


class ShopList(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_in_shops_list', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shops_list', verbose_name='Рецепты')

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.recipe}'

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупак'


class Favorite(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorits', verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorits', verbose_name='Избранный рецепты')

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.recipe}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
