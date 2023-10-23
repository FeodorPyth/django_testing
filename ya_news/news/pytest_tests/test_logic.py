import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, id_for_args, form_data):
    before_operation_count = Comment.objects.count()
    url = reverse('news:detail', args=id_for_args)
    response = client.post(url, data=form_data)
    after_operation_count = Comment.objects.count()
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert before_operation_count == after_operation_count


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client, author, news, id_for_args, form_data
):
    expected_count = Comment.objects.count() + 1
    url = reverse('news:detail', args=id_for_args)
    response = author_client.post(url, data=form_data)
    after_operation_count = Comment.objects.count()
    assert expected_count == after_operation_count
    new_comment = Comment.objects.get()
    assertRedirects(response, f'{url}#comments')
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(id_for_args, admin_client):
    before_operation_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=id_for_args)
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
        author_client, id_for_args_comment, form_data, id_for_args, comment
):
    url = reverse('news:edit', args=id_for_args_comment)
    response = author_client.post(url, form_data)
    expected_url = reverse('news:detail', args=id_for_args)
    assertRedirects(response, f'{expected_url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_reader_cant_edit_comment(
        admin_client, form_data, comment, id_for_args_comment
):
    url = reverse('news:edit', args=id_for_args_comment)
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(
        author_client, comment, id_for_args_comment, id_for_args
):
    expected_count = Comment.objects.count() - 1
    url = reverse('news:delete', args=id_for_args_comment)
    response = author_client.post(url)
    after_operation_count = Comment.objects.count()
    expected_url = reverse('news:detail', args=id_for_args)
    assertRedirects(response, f'{expected_url}#comments')
    assert expected_count == after_operation_count


def test_reader_cant_delete_comment(
        admin_client, comment, id_for_args_comment
):
    expected_count = Comment.objects.count()
    url = reverse('news:delete', args=id_for_args_comment)
    response = admin_client.post(url)
    after_operation_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == after_operation_count
