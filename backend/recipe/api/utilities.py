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
    shop_list = list(user.shopping_list.values(
        'recipe__ingredientrecord__ingredient__name',
        'recipe__ingredientrecord__amount',
        'recipe__ingredientrecord__ingredient__measurement_unit',
    ))
    print(shop_list)
    wishlist = []
    ingredients_list = {}
    for data in shop_list:
        name = data['recipe__ingredientrecord__ingredient__name']
        amount = data['recipe__ingredientrecord__amount']
        measurement_unit = data['recipe__ingredientrecord__ingredient__measurement_unit']
        if name not in ingredients_list:
            ingredients_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount,
            }
        else:
            ingredients_list[name]["amount"] += ingredients_list[name]['amount']

    for name, data in ingredients_list.items():

        wishlist.append(
            f"{name} - {data['amount']} {data['measurement_unit']}\n"
        )
    response = HttpResponse(wishlist, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="ShoppingList.txt"'
    return response
