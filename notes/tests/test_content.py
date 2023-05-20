from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from notes.models import Note

User = get_user_model()


class ContentTest(TestCase):
    """Тестирование контента"""

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

    def test_note_in_list_for_different_user(self):
        """
        Тестирование наличия заметки на странице списка заметок автора и, что
          заметки одного пользователя не попадают на страницу списка друго
            пользователя.
        """
        users_content = (
            (self.author, True),
            (self.user, False),
        )
        for user, content in users_content:
            self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                if content:
                    self.assertIn(self.notes, object_list)
                else:
                    self.assertNotIn(self.notes, object_list)

    def test_page_contains_form(self):
        """Тестирование наличия формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,))
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
