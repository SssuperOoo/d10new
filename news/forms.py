from django import forms
from .models import Post
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django import forms
from .models import Post, Author, Category



class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user
class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 100}),min_length=4, label= 'Текст поста')
    title = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 30}), label='Заголовок')
    author = forms.ModelChoiceField(queryset=Author.objects.all(), label='Автор')
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), label='Категория')

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'category',
            'author'
        ]

    def clean_text(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        text = cleaned_data.get("text")

        if title == text:
            raise ValidationError(
            "Заголовок не должен быть идентичным тексту."
            )
        if title[0].islower():
            raise ValidationError(
                "Название должно начинаться с заглавной буквы."
            )
        return text