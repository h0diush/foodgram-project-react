from drf_extra_fields.fields import Base64ImageField
from foodgram import settings
from rest_framework import serializers

from ..models import (Favorite, Follow, Ingredient, IngredientRecord, Recipe,
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
        recipes = Recipe.objects.filter(author__username=obj.username)[
            :settings.RECIPES_LIMIT]
        request = self.context.get('request')
        context = {'request': request}
        return RecipeFollowSerializer(
            recipes,
            many=True,
            context=context).data


class RecipeFavoriteOrShopList(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class IngredientInRecipeSerializerToCreateRecipe(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecord
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializers(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField('favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_cart')

    class Meta:
        model = Recipe
        fields = '__all__'

    def favorited(self, obj):
        try:
            request = self.context.get('request')
            if request is None or request.user.is_anonymous:
                return False
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        except TypeError:
            return False

    def shopping_cart(self, obj):
        try:
            request = self.context.get('request')
            if request is None or request.user.is_anonymous:
                return False
            return ShopList.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        except TypeError:
            return False

    def get_ingredients(self, obj):
        qs = IngredientRecord.objects.filter(recipe=obj)
        return IngredientInRecipeSerializerToCreateRecipe(qs, many=True).data


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializers(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField('favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShopList.objects.filter(user=request.user, recipe=obj).exists()

    def get_ingredients(self, obj):
        qs = IngredientRecord.objects.filter(recipe=obj)
        return IngredientInRecipeSerializerToCreateRecipe(qs, many=True).data


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        for ingredient in ingredients_data:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингридиента должно быть больше нуля!')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            amount = ingredient['amount']
            IngredientRecord.objects.create(
                ingredient=ingredient_model,
                recipe=recipe,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        for ingredient in ingredient_data:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингридиента должно быть больше нуля!')
        IngredientRecord.objects.filter(recipe=instance).delete()
        for new_ingredient in ingredient_data:
            IngredientRecord.objects.create(
                ingredient=Ingredient.objects.get(id=new_ingredient['id']),
                recipe=instance,
                amount=new_ingredient['amount']
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
