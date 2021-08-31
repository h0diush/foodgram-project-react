import django_filters as filters

from ..models import Ingredients


class IngredientNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name', 'measurement_unit')


class RecipeFilter(filters.FilterSet):

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

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


class FollowFilter(filters.FilterSet):

    recipes_limit = filters.NumberFilter(method="recipes_limit_filter")

    def recipes_limit_filter(self, queryset, name, value):
        qs = queryset.recipes(value)
        return qs
