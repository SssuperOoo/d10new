from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter, ModelMultipleChoiceFilter, \
    ChoiceFilter, NumberFilter
import django_filters as filters
from .models import Post, Comment, Category, PostCategory, Author
from django.forms.widgets import DateInput


# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.
class PostFilter(FilterSet):
    author = ModelChoiceFilter(
        field_name='author',
        queryset=Author.objects.all(),  #
        label='Автор',
        empty_label='Все авторы'  # Опционально: заголовок для пустого выбора
    )

    post_title = CharFilter(
        field_name='title',
        label='Заголовок',
        lookup_expr='icontains'
    )
    date = filters.DateFilter(
        field_name='post_time',
        lookup_expr='gte',
        label='Date',
        widget=DateInput(
            attrs={'type': 'date'},
        ),
    )
