# news/tests/test_trial.py
import pytest
from news.models import News


@pytest.mark.django_db
class TestNews:
    def test_successful_creation(self, news):
        news_count = News.objects.count()
        assert news_count == 1

    def test_title(self, news):
        assert news.title == 'Заголовок новости'


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок новости',
        text='Тестовый текст',
    )
