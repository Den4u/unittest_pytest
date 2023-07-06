from http import HTTPStatus

import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (('news:home', None),
     ('users:login', None),
     ('users:logout', None),
     ('users:signup', None),
     ('news:detail', pytest.lazy_fixture('slug_for_args')),),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (('news:edit', pytest.lazy_fixture('slug_for_comment')),
     ('news:delete', pytest.lazy_fixture('slug_for_comment')),),
)
def test_pages_availability_for_auth_user(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    [
        ('news:edit', pytest.lazy_fixture('slug_for_args')),
        ('news:delete', pytest.lazy_fixture('slug_for_args')),
    ],
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'))
def test_pages_availability_for_different_users(
        name, slug_for_comment, admin_client
):
    url = reverse(name, args=slug_for_comment)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
