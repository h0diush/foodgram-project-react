from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    UserFollowView, UserViewSet)

router = DefaultRouter()


router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='user-list')


urlpatterns = [
    path('users/subscriptions/', UserFollowView.as_view(), name='subscriptions'),
    path('', include(router.urls)),
    
]
