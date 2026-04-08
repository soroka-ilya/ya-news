# news/tests/test_logic.py
from http import HTTPStatus
import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCommentCreation:
    COMMENT_TEXT = 'Текст комментария'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.news = News.objects.create(title='Заголовок', text='Текст')
        self.url = reverse('news:detail', args=(self.news.id,))
        self.user = User.objects.create(username='Мимо Крокодил')
        self.form_data = {'text': self.COMMENT_TEXT}

    def test_anonymous_user_cant_create_comment(self, client):
        client.post(self.url, data=self.form_data)
        comments_count = Comment.objects.count()
        assert comments_count == 0

    def test_user_can_create_comment(self, client):
        client.force_login(self.user)
        response = client.post(self.url, data=self.form_data)
        assert response.url == f'{self.url}#comments'
        assert response.status_code == HTTPStatus.FOUND
        comments_count = Comment.objects.count()
        assert comments_count == 1
        comment = Comment.objects.get()
        assert comment.text == self.COMMENT_TEXT
        assert comment.news == self.news
        assert comment.author == self.user

    def test_user_cant_use_bad_words(self, client):
        client.force_login(self.user)
        bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
        response = client.post(self.url, data=bad_words_data)
        form = response.context['form']
        assert form.errors.get('text') == [WARNING]
        comments_count = Comment.objects.count()
        assert comments_count == 0


@pytest.mark.django_db
class TestCommentEditDelete:
    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.news = News.objects.create(title='Заголовок', text='Текст')
        news_url = reverse('news:detail', args=(self.news.id,))
        self.url_to_comments = news_url + '#comments'
        self.author = User.objects.create(username='Автор комментария')
        self.reader = User.objects.create(username='Читатель')
        self.comment = Comment.objects.create(
            news=self.news,
            author=self.author,
            text=self.COMMENT_TEXT
        )
        self.edit_url = reverse('news:edit', args=(self.comment.id,))
        self.delete_url = reverse('news:delete', args=(self.comment.id,))
        self.form_data = {'text': self.NEW_COMMENT_TEXT}

    def test_author_can_delete_comment(self, client):
        client.force_login(self.author)
        comments_count = Comment.objects.count()
        assert comments_count == 1
        response = client.delete(self.delete_url)
        assert response.url == self.url_to_comments
        assert response.status_code == HTTPStatus.FOUND
        comments_count = Comment.objects.count()
        assert comments_count == 0

    def test_author_can_edit_comment(self, client):
        client.force_login(self.author)
        response = client.post(self.edit_url, data=self.form_data)
        assert response.url == self.url_to_comments
        self.comment.refresh_from_db()
        assert self.comment.text == self.NEW_COMMENT_TEXT

    def test_user_cant_edit_comment_of_another_user(self, client):
        client.force_login(self.reader)
        response = client.post(self.edit_url, data=self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        self.comment.refresh_from_db()
        assert self.comment.text == self.COMMENT_TEXT
