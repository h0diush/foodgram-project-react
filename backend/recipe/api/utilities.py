import csv

from django.http import HttpResponse
from rest_framework import response, status

from ..models import Follow, IngredientRecord, Recipe, ShopList, User
from .serializers import RecipeFavoriteOrShopList, UserFollowSerializer


def _get_recipe_in_shop_list_and_favorite(recipe, user, request, obj):

    serializer = RecipeFavoriteOrShopList(Recipe.objects.get(pk=recipe.id))

    if user.is_authenticated:
        if request.method == 'GET':
            shop_list, created = obj.objects.get_or_create(
                user=user, recipe=recipe)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            ) if created else  \
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
                        if obj == ShopList else {
                            "detail": "Рецепт успешно удален из избранного"
                    }),
                    status=status.HTTP_204_NO_CONTENT
                )
            except BaseException:
                return response.Response(
                    {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST)

        return response.Response(
            {"detail": "Учетные данные не были предоставлены."},
            status=status.HTTP_403_FORBIDDEN
        )


def _user_subscription_to_author(author, user, request, obj):

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
                return response.Response(
                    "Успешная отписка", status=status.HTTP_204_NO_CONTENT)
            except BaseException:
                return response.Response(
                    {"errors": "string"}, status=status.HTTP_400_BAD_REQUEST)
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
    shop_list = user.shops_list.all()
    buying_list = {}
    for record in shop_list:
        recipe = record.recipe
        for ingredient in IngredientRecord.objects.filter(recipe=recipe):
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in buying_list:
                buying_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                buying_list[name]['amount'] = (buying_list[name]['amount']
                                               + amount)
    wishlist = []
    for name, data in buying_list.items():
        wishlist.append(
            f"{name} ({data['measurement_unit']}) - {data['amount']} \n")
    response = HttpResponse(wishlist, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="ShoppingList.txt"'
    return response
