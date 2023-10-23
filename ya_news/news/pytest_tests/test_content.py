import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, news_for_count):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_for_count):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_form_order(news, id_for_args, client, comment_for_count):
    url = reverse('news:detail', args=id_for_args)
    response = client.get(url)
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
@pytest.mark.django_db
def test_access_for_form(
    id_for_args, parametrized_client, expected_result
):
    url = reverse('news:detail', args=id_for_args)
    response = parametrized_client.get(url)
    possible_result = 'form' in response.context
    assert possible_result == expected_result
