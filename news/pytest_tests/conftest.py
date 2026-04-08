import pytest

from datetime import datetime, timedelta
from django.test.client import Client
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def client():
    """Обычный неавторизованный клиент."""
    return Client()


@pytest.fixture
def author_client(author):
    """Авторизованный клиент от имени автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Авторизованный клиент от имени не-автора."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок новости',
        text='Тестовый текст',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def news_id_for_args(news):
    """Возвращает кортеж с id новости для reverse()."""
    return (news.id,)


@pytest.fixture
def comment_id_for_args(comment):
    """Возвращает кортеж с id комментария для reverse()."""
    return (comment.id,)


@pytest.fixture
def news_list():
    """Создает 11 новостей для проверки пагинации и сортировки."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {i}',
            text='Текст',
            date=today - timedelta(days=i)
        )
        for i in range(11)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment_list(news, author):
    """Создает несколько комментариев с разным временем для проверки сортировки."""
    for i in range(3):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {i}'
        )
        comment.created = timezone.now() + timedelta(minutes=i)
        comment.save()
