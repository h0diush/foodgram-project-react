from rest_framework import serializers

from ..models import Favorite, Follow, Ingredients, Recipe, ShopList, Tag, User


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def validate(self, attrs):
        l_name, f_name, email = attrs['last_name'], attrs['first_name'], attrs['email']
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


class IngredientsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    tags = TagSerializers(read_only=True, many=True)
    ingredients = IngredientsCreateSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField('favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

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


class RecipeCreateSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')


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
