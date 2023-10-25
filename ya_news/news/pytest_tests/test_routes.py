from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('home_url')),
        (pytest.lazy_fixture('detail_url')),
        (pytest.lazy_fixture('login_url')),
        (pytest.lazy_fixture('logout_url')),
        (pytest.lazy_fixture('signup_url'))
    )
)
@pytest.mark.django_db
def test_pages_availability(client, name, news):
    url = name
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('edit_url'))
    )
)
@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(
    name, parametrized_client, expected_status, id_for_args_comment
):
    url = name
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('delete_url')),
        (pytest.lazy_fixture('edit_url'))
    )
)
@pytest.mark.django_db
def test_redirects(client, name, comment, login_url):
    login_url = login_url
    url = name
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
