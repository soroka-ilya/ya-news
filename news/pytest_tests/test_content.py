import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, news_list):
    """Количество новостей на главной не превышает NEWS_COUNT_ON_HOME_PAGE."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    """Новости отсортированы от самых новых к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news, comment_list):
    """Комментарии на странице новости идут в хронологическом порядке."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [c.created for c in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert list(all_timestamps) == sorted_timestamps


@pytest.mark.django_db
def test_pages_contains_form(client, author_client, news, comment):
    """Проверка наличия формы для разных типов пользователей."""
    detail_url = reverse('news:detail', args=(news.id,))
    edit_url = reverse('news:edit', args=(comment.id,))

    assert 'form' not in client.get(detail_url).context

    for url in (detail_url, edit_url):
        response = author_client.get(url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
