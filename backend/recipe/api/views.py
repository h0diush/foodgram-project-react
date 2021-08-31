from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..models import Favorite, Follow, Ingredients, Recipe, ShopList, Tag, User
from .filters import IngredientNameFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadAnllyUser, IsAuthorRecipeOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          ShowRecipeSerializer, TagSerializers,
                          UserFollowSerializer)
from .utilities import (_download_shop_list,
                        _get_recipe_in_shop_list_and_favorite,
                        _user_subscription_to_author)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializers
    pagination_class = None
    queryset = Tag.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    permission_classes = [IsAdminOrReadAnllyUser]


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredients.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    filterset_class = IngredientNameFilter


class RecipeViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAuthorRecipeOrReadOnly]
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
        return _get_recipe_in_shop_list_and_favorite(
            recipe, user, request, ShopList)

    @action(
        methods=['GET', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe, user = self._get_user_and_recipe(request)
        return _get_recipe_in_shop_list_and_favorite(
            recipe, user, request, Favorite)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        return _download_shop_list(request.user)


class UserViewSet(BaseUserViewSet):

    pagination_class = LimitPageNumberPagination

    def _get_user_and_author(self, request):
        author = self.get_object()
        user = request.user
        return author, user

    @action(detail=True,
            permission_classes=[IsAuthenticated], methods=['GET', 'DELETE'])
    def subscribe(self, request, id=None):
        author, user = self._get_user_and_author(request)
        return _user_subscription_to_author(author, user, request, Follow)


class UserFollowView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserFollowSerializer
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        return User.objects.filter(follower__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
