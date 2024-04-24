from django import template



register = template.Library()


# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.
@register.filter(name='censor')
def censor(text):
    badwords = ['редиска', 'петрушка']
    return ' '.join([i[0]+('*' * (len(i)-1)) if i in badwords else i for i in text.split()])

@register.filter
def is_author(user):
    return user.groups.filter(name='authors').exists()