import pytest

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def anonymous_client(client):
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новый тайтл',
        text='Новый текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news,
                                  author=author,
                                  text='Текст комментария')


@pytest.fixture
def slug_for_comment(comment):
    return (comment.pk,)


@pytest.fixture
def slug_for_args(news):
    return(news.pk,)


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}


@pytest.fixture
def all_news(news):
    now = timezone.now()
    all_new = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=now - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_new)


@pytest.fixture
def all_comments(news, author):
    now = timezone.now()
    for index in range(11):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Comment text {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
