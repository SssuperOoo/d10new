from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter,ModelMultipleChoiceFilter,ChoiceFilter,NumberFilter
import django_filters as filters
from .models import Product, Material


# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.

class ProductFilter(FilterSet):

    material = ModelChoiceFilter(
        field_name = 'material',
        queryset=Material.objects.all(),
        label = 'Materials',
        empty_label = 'любой материал'

    )

    search_name = CharFilter(
        field_name='name',
        label = ' Название продукта',
        lookup_expr = 'icontains'
    )

    search_quantity__gt = NumberFilter(
        field_name='quantity',
        label=' Количество продукта больше чем',
        lookup_expr='gt'
    )

    search_price__lt = NumberFilter(
        field_name='price',
        label=' Цена продукта меньше чем',
        lookup_expr='lt'
    )

    search_price__gt = NumberFilter(
        field_name='price',
        label=' Цена продукта больше чем',
        lookup_expr='gt'
    )
    # class Meta:
    #     model = Product
    #     fields = {
    #         'material' : ['exact'],
    #         'name': ['icontains'],
    #         'quantity': ['gt'],
    #         'price': ['lt', 'gt'],
    #     }
