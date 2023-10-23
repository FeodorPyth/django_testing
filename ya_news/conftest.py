from datetime import timedelta

import pytest

from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


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
