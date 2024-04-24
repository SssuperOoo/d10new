from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import *
from .filters import PostFilter
from django.urls import reverse_lazy, reverse
from .forms import PostForm
from django.shortcuts import redirect, reverse, HttpResponseRedirect, render
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives, mail_managers,send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import new_post


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    return redirect('/')
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context


class NewsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-post_time'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'

    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class CategoryList(NewsList):
    model = Post
    template_name = 'category/category_list.html'
    context_object_name = "category_list"

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk']) #отличная функция которая будет ловить ошибку, например в случае когда данной категории уже не будет
        queryset = Post.objects.filter(category =self.category).order_by('title')
        return queryset

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["is_not_subscriber"] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id = pk)
    category.subscribers.add(user)

    # Формируем текст и HTML для письма
    subject = 'Подписка на категорию'
    context = {'user_name': user.username, 'category_name': category.name}
    html_content = render_to_string('category/subscribe_email.html', context)

    # Отправляем письмо
    msg = EmailMultiAlternatives(subject, from_email = 'olegnasyrov.o@yandex.ru', to = [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    message = 'Вы успешно подписались на рассылку новостей данной категории'
    return render(request, 'category/subscribe.html',{'category': category, 'message':message})

class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — product.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'

class PostSearch(ListView):
    model = Post
    ordering = '-post_time'
    template_name = 'news_search.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

class NewsCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news_create.html' # тут создается Новость по default ид модели

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        new_post.delay(post.pk)
        return super().form_valid(form)
    def handle_no_permission(self):
        # Выводим сообщение об ошибке
        messages.error(self.request, "Вы не являетесь автором")
        # Перенаправляем на страницу /
        return redirect('/')
class ArticleCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    permission_required = ('news.add_post',)
    model = Post
    template_name = 'article_create.html'
    form_class = PostForm
    # success_url = reverse_lazy('post_detail')

    def form_valid(self, form):
        form.instance.post_type = 'AR'  # Задаем тип записи как "статья"
        return super().form_valid(form)

    def handle_no_permission(self):
        # Выводим сообщение об ошибке
        messages.error(self.request, "Вы не являетесь автором")
        # Перенаправляем на страницу /
        return redirect('/')

class NewsUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post_type != 'NEW':  # Проверяем, что тип записи является новостью
            raise Http404("Страница не найдена")  # Отправляем 404 ошибку
        return super().dispatch(request, *args, **kwargs)

class ArticleUpdate(PermissionRequiredMixin,LoginRequiredMixin,UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post_type != 'AR':  # Проверяем, что тип записи является статьей
            raise Http404("Страница не найдена")  # Отправляем 404 ошибку
        return super().dispatch(request, *args, **kwargs)

class NewsDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post_type != 'NEW':  # Проверяем, что тип записи является новостью
            raise Http404("Страница не найдена, такой новости нет")  # Отправляем 404 ошибку
        return super().dispatch(request, *args, **kwargs)

class ArticlesDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'articles_delete.html'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.post_type != 'AR':  # Проверяем, что тип записи является новостью
            raise Http404("Страница не найдена, такой статьи нет")  # Отправляем 404 ошибку
        return super().dispatch(request, *args, **kwargs)