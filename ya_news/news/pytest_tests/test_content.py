import pytest
from django.conf import settings

from conftest import URL
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, news_for_count):
    url = URL['home']
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_for_count):
    url = URL['home']
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_form_order(news, client, comment_for_count):
    url = URL['detail']
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_access_for_form(
    id_for_args, admin_client, client
):
    url = URL['detail']
    response = client.get(url)
    admin_response = admin_client.get(url)
    possible_result = 'form' not in response.context
    assert (possible_result
            and isinstance(admin_response.context['form'], CommentForm))
