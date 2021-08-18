import django_filters as filters

from ..models import Ingredients


class IngredientsFilter(filters.FilterSet):

    name = filters.CharFilter(
        field_name='name', lookup_expr='contains'
    )

    class Meta:
        model = Ingredients
        fields = ['name']
