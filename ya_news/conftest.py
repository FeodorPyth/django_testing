from datetime import timedelta

import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


URL = {
    'home': reverse('news:home'),
    'detail': reverse('news:detail', args=(1,)),
    'edit': reverse('news:edit', args=(1,)),
    'delete': reverse('news:delete', args=(1,)),
    'login': reverse('users:login'),
    'logout': reverse('users:logout'),
    'signup': reverse('users:signup'),
}


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(news, comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(news, comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор Комментария')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )
    return comment


@pytest.fixture
def id_for_args_comment(comment):
    return comment.id,


@pytest.fixture
def news():
    news = News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
    )
    return news


@pytest.fixture
def id_for_args(news):
    return news.id,


@pytest.fixture
def news_for_count():
    now = timezone.now()
    News.objects.bulk_create(
        News(title='Новость номер {index}',
             text='Текст комментария с номером',
             date=now - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment_for_count(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data(author, news):
    return {
        'text': 'Новый комментарий',
        'author': author,
        'news': news
    }
