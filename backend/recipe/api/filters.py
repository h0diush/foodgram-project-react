import django_filters as filters

from ..models import Ingredient


class IngredientNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(filters.FilterSet):

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    is_favorited = filters.BooleanFilter(
        field_name='favorites__recipe',
        method='filter_favorited',
        lookup_expr='isnull'
    )

    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping_list__recipe',
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
            shopping_list__user=self.request.user
        )

    def filter_favorited(self, queryset, name, value):
        lookup = '__'.join([name, 'isnull'])
        return queryset.exclude(
            **{lookup: value}
        ).filter(
            favorites__user=self.request.user
        )
