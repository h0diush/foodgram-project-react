import csv

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import response, status

from ..models import Follow, Recipe, ShopList, User
from .serializers import RecipeFavoriteOrShopList, UserFollowSerializer


def _get_recipe_in_shop_list_and_favorite(recipe, user, request, obj):

    serializer = RecipeFavoriteOrShopList(
        get_object_or_404(Recipe, pk=recipe.id))

    if request.method == 'GET':
        shop_list, created = obj.objects.get_or_create(
            user=user, recipe=recipe)
        if created:
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return response.Response({"errors": "string"},
                                 status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        shop_list = get_object_or_404(obj, user=user, recipe=recipe)
        shop_list.delete()
        return response.Response(
            ({"detail": "Рецепт успешно удален из списка покупок"}
                if obj == ShopList else {
                    "detail": "Рецепт успешно удален из избранного"
            }),
            status=status.HTTP_204_NO_CONTENT
        )


def _user_subscription_to_author(author, user, request, obj):

    serializer = UserFollowSerializer(
        get_object_or_404(User, username=author.username))

    if request.method == 'GET':
        follow, created = obj.objects.get_or_create(
            author=author, user=user
        )
        if created:
            return response.Response(
                serializer.data, status=status.HTTP_200_OK
            )

        return response.Response({"errors": "string"},
                                 status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        follow = get_object_or_404(Follow, author=author, user=user)
        follow.delete()
        return response.Response(
            "Успешная отписка", status=status.HTTP_204_NO_CONTENT)


def _download_shop_list(user):
    response_download = HttpResponse(content_type='text/csv')
    writer = csv.writer(response_download)
    writer.writerow(
        [
            'Название',
            'Количество',
            'Единица измерения'
        ])
    shop_list = list(user.shopping_list.values(
        'recipe__ingredients__name',
        'recipe__ingredients__ingredientrecord__amount',

        'recipe__ingredients__measurement_unit',
    ))
    wishlist = []
    for data in shop_list:
        wishlist.append(
            f"{data['recipe__ingredients__name']} "
            f"({data['recipe__ingredients__ingredientrecord__amount']})"
            f" - {data['recipe__ingredients__measurement_unit']} \n")
    response = HttpResponse(wishlist, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="ShoppingList.txt"'
    return response
