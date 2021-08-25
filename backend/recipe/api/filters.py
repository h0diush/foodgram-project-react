import django_filters as filters

from ..models import Ingredients


class IngredientsFilter(filters.FilterSet):

    name = filters.CharFilter(
        field_name='name', lookup_expr='contains'
    )

    class Meta:
        model = Ingredients
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='favorits__recipe',
        method='filter_favorited',
        lookup_expr='isnull'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shops_list__recipe',
        method='filter_shopping_cart',
        lookup_expr='isnull'
    )
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='contains'
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='contains'
    )

    limit = filters.CharFilter(
        method='recipe_limit',
        lookup_expr='contains'
    )

    def filter_shopping_cart(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        return queryset.exclude(
            **{lookup: value}
        ).filter(
            shops_list__user=self.request.user
        )

    def filter_favorited(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        return queryset.exclude(
            **{lookup: value}
        ).filter(
           favorits__user=self.request.user
        )

    def recipe_limit(self, queryset, name, value):
        count = int(value)
        return queryset[:count]
