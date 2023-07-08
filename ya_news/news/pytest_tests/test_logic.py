from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, slug_for_args, form_data):
    expected_count = Comment.objects.count()
    url = reverse('news:detail', args=slug_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert expected_count == comments_count


def test_user_can_create_comment(
        admin_user, admin_client, news, form_data):
    expected_count = Comment.objects.count() + 1
    url = reverse('news:detail', args=[news.pk])
    response = admin_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    new_comment = Comment.objects.get()
    expected_url = url + '#comments'
    assertRedirects(response, expected_url)
    assert expected_count == comments_count
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == admin_user


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, slug_for_args):
    expected_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то text, {BAD_WORDS[0]}, еще text'}
    url = reverse('news:detail', args=slug_for_args)
    response = admin_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert expected_count == comments_count


def test_author_can_edit_comment(
        author_client, slug_for_args, comment, form_data):
    expected_count = Comment.objects.count()
    url = reverse('news:edit', args=[comment.pk])
    response = author_client.post(url, data=form_data)
    expected_url = reverse('news:detail', args=slug_for_args) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert comment.text == form_data['text']
    assert expected_count == comments_count


def test_author_can_delete_comment(
        author_client, slug_for_args, slug_for_comment):
    expected_count = Comment.objects.count() - 1
    url = reverse('news:delete', args=slug_for_comment)
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=slug_for_args) + '#comments'
    comments_count = Comment.objects.count()
    assertRedirects(response, expected_url)
    assert expected_count == comments_count


def test_other_user_cant_edit_comment(
        admin_client, slug_for_args, comment, form_data):
    expected_count = Comment.objects.count()
    url = reverse('news:edit', args=[comment.pk])
    response = admin_client.post(url, data=form_data)
    old_comment = comment.text
    comment.refresh_from_db()
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == old_comment
    assert expected_count == comments_count


def test_other_user_cant_delete_comment(
        admin_client, slug_for_args, slug_for_comment):
    expected_count = Comment.objects.count()
    url = reverse('news:delete', args=slug_for_comment)
    response = admin_client.post(url)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert expected_count == comments_count
