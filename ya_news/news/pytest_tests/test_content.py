import pytest

from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response .context['object_list']
    comments_count = len(object_list)
    assert comments_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.parametrize(
    'username, is_permitted', ((pytest.lazy_fixture('admin_client'), True),
                               (pytest.lazy_fixture('client'), False))
)
def test_comment_form_availability_for_different_users(
        slug_for_args, username, is_permitted):
    url = reverse('news:detail', args=slug_for_args)
    response = username.get(url)
    assert ('form' in response.context) is is_permitted


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = list(response.context['object_list'])
    sorted_list_of_news = sorted(object_list,
                                 key=lambda news: news.date, reverse=True)
    assert object_list == sorted_list_of_news


@pytest.mark.django_db
@pytest.mark.usefixtures('all_comments')
def test_comments_order(client, slug_for_args):
    url = reverse('news:detail', args=slug_for_args)
    response = client.get(url)
    object_list = list(response.context['news'].comment_set.all())
    sorted_list_of_comments = sorted(object_list,
                                     key=lambda comment: comment.created)
    assert object_list == sorted_list_of_comments
