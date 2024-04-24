
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView




urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
  # Делаем так, чтобы все адреса из нашего приложения (simpleapp/urls.py)
   # подключались к главному приложению с префиксом products/.
    path('', include('simpleapp.urls')),
    path('', include('news.urls')),
    path('accounts/', include('allauth.urls')),
    path('sign/', include('sign.urls')),
    path('', include('protect.urls')),
]