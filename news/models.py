
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import timezone
from django.db.models.functions import Coalesce
from django.urls import reverse

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = Post.objects.filter(author = self).aggregate(pr=Coalesce(Sum('rating'),0))['pr'] # отфильтровали по автору, с помощью агрегатора
        # взяли Сумму по ключу rating и получили словарь, в котором заменили
        # ключ на pr  получили значение по ключу.
        comments_rating = Comment.objects.filter(user = self.user).aggregate(cr=Coalesce(Sum('rating'),0))['cr']
        posts_comments_rating = Comment.objects.filter(post__author=self).aggregate(pcr = Coalesce(Sum('rating'),0))['pcr']

        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating
        self.save()

        print(self.rating)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=250,unique=True)
    subscribers = models.ManyToManyField(User, blank=True, null=True, related_name="categories")

    def __str__(self):
        return self.name
class Post(models.Model):
    article = "AR"
    news = "NEW"
    ARTICLES = [(article, 'Статья'),
                (news, 'Новость')]

    post_type = models.CharField(max_length=3, choices=ARTICLES, default='NEW')
    post_time = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=250)
    text = models.TextField()
    rating = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, through="PostCategory")

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating += 1
        self.save()

    def preview(self):
        return f'{self.text[0:124]}...'

    def __str__(self):
        return f'{self.post_type}, {self.title[:20]}, {self.text}'


    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

class PostCategory(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # def __str__(self):
    #     return f'{self.category.name}'
    def __str__(self):
        return f'{self.category} : {self.post.title}'


class Comment(models.Model):
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def like(self):
        self.rating += 1
        self.save()


    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return self.text[:100]