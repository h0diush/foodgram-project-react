import csv

from django.http import HttpResponse
from rest_framework import response, status

from ..models import Follow, Recipe, ShopList, User
from .serializers import UserFollowSerializer, RecipeFavoriteOrShopList


def _get_recipe_in_shop_list_and_favorite(recipe, user, request, obj):

    serializer = RecipeFavoriteOrShopList(Recipe.objects.get(pk=recipe.id))

    if user.is_authenticated:
        if request.method == 'GET':
            shop_list, created = obj.objects.get_or_create(
                user=user, recipe=recipe)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED) if created else  \
                response.Response({"errors": "string"},
                                  status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            try:
                shop_list = obj.objects.get(
                    user=user, recipe=recipe
                )
                shop_list.delete()
                return response.Response(
                    ({"detail": "Рецепт успешно удален из списка покупок"}
                        if obj == ShopList else {"detail": "Рецепт успешно удален из избранного"}),
                    status=status.HTTP_204_NO_CONTENT
                )
            except:
                return response.Response({"errors": "string"}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(
            {"detail": "Учетные данные не были предоставлены."},
            status=status.HTTP_403_FORBIDDEN
        )


def _user_subscription_to_post_author(author, user, request, obj):

    if request.user.is_authenticated:
        if request.method == 'GET':
            follow, created = obj.objects.get_or_create(
                author=author, user=user
            )
            serializer = UserFollowSerializer(
                User.objects.get(username=author.username))
            return (
                response.Response(serializer.data, status=status.HTTP_200_OK)
                if created else
                response.Response({"errors": "string"},
                                  status=status.HTTP_400_BAD_REQUEST)
            )
        elif request.method == 'DELETE':
            try:
                follow = Follow.objects.get(author=author, user=user)
                follow.delete()
                return response.Response("Успешная отписка", status=status.HTTP_204_NO_CONTENT)
            except:
                return response.Response({"errors": "string"}, status=status.HTTP_400_BAD_REQUEST)
    return response.Response(
        {"detail": "Учетные данные не были предоставлены."},
        status=status.HTTP_403_FORBIDDEN
    )


def _download_shop_list(user):
    response_download = HttpResponse(content_type='text/csv')
    writer = csv.writer(response_download)
    writer.writerow(
        [
            'Название',
            'Количество',
            'Единица измерения'
        ])
    recipes = Recipe.objects.filter(shops_list__user=user)
    for recipe in recipes:
        for ingredient in recipe.ingredients.all():
            writer.writerow(
                [
                    ingredient.name,
                    ingredient.amount,
                    ingredient.measurement_unit
                ]
            )
    response_download['Content-Disposition'] = f'attachment; filename="shopping_list.csv"'
    return response_download
