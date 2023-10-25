from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, detail_url, login_url
):
    before_operation_count = Comment.objects.count()
    url = detail_url
    response = client.post(url, data=form_data)
    after_operation_count = Comment.objects.count()
    login_url = login_url
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert before_operation_count == after_operation_count


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client, author, news, form_data, detail_url
):
    expected_count = Comment.objects.count() + 1
    url = detail_url
    response = author_client.post(url, data=form_data)
    after_operation_count = Comment.objects.count()
    assert expected_count == after_operation_count
    new_comment = Comment.objects.get()
    assertRedirects(response, f'{url}#comments')
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(id_for_args, admin_client, detail_url):
    before_operation_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = detail_url
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comment_count = Comment.objects.count()
    assert before_operation_count == comment_count


def test_author_can_edit_comment(
        author, news, author_client, form_data, comment, edit_url, detail_url
):
    url = edit_url
    response = author_client.post(url, form_data)
    expected_url = detail_url
    assertRedirects(response, f'{expected_url}#comments')
    comment.refresh_from_db()
    assert comment.news == form_data['news']
    assert comment.author == form_data['author']
    assert comment.text == form_data['text']


def test_reader_cant_edit_comment(admin_client, form_data, comment, edit_url):
    url = edit_url
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
        author_client, comment, delete_url, detail_url
):
    expected_count = Comment.objects.count() - 1
    url = delete_url
    response = author_client.post(url)
    after_operation_count = Comment.objects.count()
    expected_url = detail_url
    assertRedirects(response, f'{expected_url}#comments')
    assert expected_count == after_operation_count


def test_reader_cant_delete_comment(admin_client, comment, delete_url):
    expected_count = Comment.objects.count()
    url = delete_url
    response = admin_client.post(url)
    after_operation_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == after_operation_count
