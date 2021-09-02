from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from ..models import (Favorite, Follow, IngredientRecord, Ingredient, Recipe,
                      ShopList, Tag, User)


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, attrs):
        last_name, first_name, email = (
            attrs['last_name'], attrs['first_name'], attrs['email']
        )
        if last_name == '' or first_name == '':
            raise serializers.ValidationError('This field is required')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'This email is already in use by another user.')
        return attrs

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            last_name=validated_data['last_name'],
            first_name=validated_data['first_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField('follow')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def follow(self, obj):
        request = self.context.get('request')
        if (Follow.objects.filter(
                author__username=obj.username,
                user__username=request.user.username
        ).exists()
                or obj.username == request.user.username):
            return True
        return False


class TagSerializers(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecord
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializers(read_only=True, many=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_amounts',
        many=True, read_only=True,
    )
    is_favorited = serializers.SerializerMethodField('favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time'
                  )

    def favorited(self, obj):
        request = self.context.get('request')
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def shopping_cart(self, obj):
        request = self.context.get('request')
        return ShopList.objects.filter(user=request.user, recipe=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('Убедитесь, что значение количества '
                     'ингредиента больше 0')
                )
            id = ingredient.get('id')
            if id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент в рецепте не должен повторяться.'
                )
            ingredients_set.add(id)
        data['ingredients'] = ingredients

        return data

    @transaction.atomic
    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags = self.initial_data.get('tags')

        for tag_id in tags:
            recipe.tags.add(get_object_or_404(Tag, pk=tag_id))

        for ingredient in ingredients:
            IngredientRecord.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = self.initial_data.get('tags')

        for tag_id in tags:
            instance.tags.add(get_object_or_404(Tag, pk=tag_id))

        IngredientRecord.objects.filter(recipe=instance).delete()
        for ingredient in validated_data.get('ingredients'):
            ingredients_amounts = IngredientRecord.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            ingredients_amounts.save()

        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        instance.refresh_from_db()

        return instance


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField('follow')
    recipes_count = serializers.SerializerMethodField('count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'is_subscribed',
                  'recipes_count', )

    def follow(self, obj):
        return Follow.objects.filter(author__username=obj.username).exists()

    def count(self, obj):
        count = Recipe.objects.filter(author__username=obj.username).count()
        return count

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit is None:
            result = Recipe.objects.filter(author__username=obj.username)
        else:
            recipes_limit = int(request.query_params.get("recipes_limit"))
            result = Recipe.objects.filter(author__username=obj.username)[
                :recipes_limit]
        return RecipeFollowSerializer(result, many=True).data


class RecipeFavoriteOrShopList(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
