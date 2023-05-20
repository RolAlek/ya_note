from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from notes.models import Note

User = get_user_model()


class RoutesTest(TestCase):
    """Тестирование маршрутизации."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.notes = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )
        cls.user = User.objects.create(username='Пользователь')

    def test_pages_availability(self):
        """
        Тестирование доступности домашней страницы и страниц авторизации
          анонимному пользователю.
        """
        urls = (
            'notes:home', 'users:login', 'users:logout', 'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Тестирование доступности страниц добавления заметки, списка заметок и
          страницы успешного добавления заметки для авторизованного
            пользователя.
        """
        urls = (
            'notes:add', 'notes:list', 'notes:success'
        )
        self.client.force_login(self.user)
        for name in urls:
            with self.subTest(user=self.user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_avaliability_for_detail_and_manage_note(self):
        """
        Тестрирование доступа к страницам заметки и управления заметками
          только для автора.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail', 'notes:edit', 'notes:delete'
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Тестирование gеренаправления анонимного пользователя на страницу
          аутентификации пользователя.
        """
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.notes.slug,)),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
