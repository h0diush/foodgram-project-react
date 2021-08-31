from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from ..models import (Favorite, Follow, IngredientRecord, Ingredients, Recipe,
                      ShopList, Tag, User)


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, attrs):
        l_name, f_name, email = \
            attrs['last_name'], attrs['first_name'], attrs['email']
        if l_name == '' or f_name == '':
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
        model = Ingredients
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


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializers(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField('favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_cart')

    def favorited(self, obj):
        request = self.context.get('request')
        if Favorite.objects.filter(user=request.user, recipe=obj).exists():
            return True
        return False

    def shopping_cart(self, obj):
        request = self.context.get('request')
        if ShopList.objects.filter(user=request.user, recipe=obj).exists():
            return True
        return False

    def get_ingredients(self, obj):
        qs = IngredientRecord.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(qs, many=True).data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')


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
        if Favorite.objects.filter(user=request.user, recipe=obj).exists():
            return True
        return False

    def shopping_cart(self, obj):
        request = self.context.get('request')
        if ShopList.objects.filter(user=request.user, recipe=obj).exists():
            return True
        return False

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                "Рецепт не может быть без тегов."
            )

        unique_tags = set(tags)
        if len(unique_tags) != len(tags):
            raise serializers.ValidationError(
                "Массиов тегов должен быть уникальным."
            )
        return tags

    def validate_ingredients(self, recipeingredients):
        if not recipeingredients:
            raise serializers.ValidationError(
                "Рецепт не может быть без ингредиентов."
            )

        not_unique_ingredients = [
            recipeingredient["ingredient"].id
            for recipeingredient in recipeingredients
        ]
        unique_ingredients = set(not_unique_ingredients)

        not_unique_ingredients_amount = len(not_unique_ingredients)
        unique_ingredients_amount = len(unique_ingredients)

        if unique_ingredients_amount != not_unique_ingredients_amount:
            raise serializers.ValidationError(
                "Каждый ингредиент в рецепте должен быть уникальным."
            )

        return recipeingredients

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

        return instance


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserFollowSerializer(serializers.ModelSerializer):

    recipes = RecipeFollowSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField('follow')
    recipes_count = serializers.SerializerMethodField('count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'recipes', 'is_subscribed',
                  'recipes_count', )

    def follow(self, obj):
        if (Follow.objects.filter(
            author__username=obj.username
        ).exists()):
            return True
        return False

    def count(self, obj):
        count = Recipe.objects.filter(author__username=obj.username).count()
        return count


class RecipeFavoriteOrShopList(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
