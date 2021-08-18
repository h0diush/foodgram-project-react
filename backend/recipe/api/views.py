from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import response, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from ..models import Favorite, Follow, Ingredients, Recipe, ShopList, Tag, User
from .filters import IngredientsFilter
from .permissions import IsAdminOrReadAnllyUser, IsAuthorRecipeOrReadOnly
from .serializers import (IngredientsCreateSerializer,
                          IngredientsListSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, TagSerializers,
                          UserFollowSerializer)
from .utilits import _get_recipe_in_shop_list_and_favorite, _user_subscription_to_post_author


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializers
    queryset = Tag.objects.all()
    permission_classes = [IsAdminOrReadAnllyUser]


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Ingredients.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
    filterset_class = IngredientsFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return IngredientsListSerializer
        return IngredientsCreateSerializer


class RecipeViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthorRecipeOrReadOnly]
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def _get_user_and_recipe(self, request):
        user = request.user
        recipe = self.get_object()
        return recipe, user

    @action(
        methods=['GET', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe, user = self._get_user_and_recipe(request)
        return _get_recipe_in_shop_list_and_favorite(recipe, user, request, ShopList)

    @action(
        methods=['GET', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe, user = self._get_user_and_recipe(request)
        return _get_recipe_in_shop_list_and_favorite(recipe, user, request, Favorite)


class UserViewSet(BaseUserViewSet):

    def _get_user_and_author(self, request):
        author = self.get_object()
        user = request.user
        return author, user

    @action(detail=True, permission_classes=[IsAuthenticated], methods=['GET', 'DELETE'])
    def subscribe(self, request, id=None):
        author, user = self._get_user_and_author(request)
        return _user_subscription_to_post_author(author, user, request, Follow)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        if request.user.is_authenticated:
            serializer = UserFollowSerializer(User.objects.filter(
                follower__user=self.request.user), many=True)
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(
            {"detail": "Учетные данные не были предоставлены."},
            status=status.HTTP_403_FORBIDDEN
        )
