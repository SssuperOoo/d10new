from django.urls import path
from .views import NewsList, PostDetail, NewsCreate, PostSearch, ArticleCreate, NewsUpdate, ArticleUpdate, NewsDelete, \
    ArticlesDelete, ProfileView, upgrade_me, CategoryList, subscribe
from django.contrib.auth import views

urlpatterns = [
    # path — означает путь.
    # В данном случае путь ко всем товарам у нас останется пустым,
    # чуть позже станет ясно почему.
    # Т.к. наше объявленное представление является классом,
    # а Django ожидает функцию, нам надо представить этот класс в виде view.
    # Для этого вызываем метод as_view.
    # path('login/', views.LoginView.as_view(), name='login'),
    path('', ProfileView.as_view()),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('posts/', NewsList.as_view(), name='post_list'),
    path('posts/<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('posts/search/', PostSearch.as_view(), name='post_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/update/', NewsUpdate.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('articles/create/', ArticleCreate.as_view(), name='articles_create'),
    path('articles/<int:pk>/update/', ArticleUpdate.as_view(), name='articles_update'),
    path('articles/<int:pk>/delete/', ArticlesDelete.as_view(), name='articles_delete'),
    path('posts/categories/<int:pk>', CategoryList.as_view(), name = 'category_list'),
    path('posts/categories/<int:pk>/subscribe', subscribe, name ='subscribe')

]
