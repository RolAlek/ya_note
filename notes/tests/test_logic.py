from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class LogicTest(TestCase):
    """Тестирование логики приложения."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.notes = Note.objects.create(
            title='Заголовок заметки',
            text='Текст хаметки',
            slug='test-slug',
            author=cls.author
        )
        cls.user = User.objects.create(username='Пользователь')
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новый заголовк',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_anonymous_user_cant_create_note(self):
        """Тестирование создания заметки анонимным пользователем."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_auth_user_can_create_note(self):
        """Тестирование создания заметки авторизованным пользователем."""
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
        """Тестирование уникальности значения поля slug."""
        self.form_data['slug'] = self.notes.slug
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.notes.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        """Тестирование автоматической генерации поля slug."""
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        new_note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Тестирование редактирования заметок автором."""
        url = reverse('notes:edit', args=(self.notes.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.notes.refresh_from_db()
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])

    def test_other_user_edit_note(self):
        """Тестирование редактирования заметки др. пользователем."""
        url = reverse('notes:edit', args=(self.notes.slug,))
        self.client.force_login(self.user)
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
        self.assertEqual(self.notes.slug, note_from_db.slug)

    def test_author_delete_note(self):
        """Тестирование удаления заметки автором."""
        url = reverse('notes:delete', args=(self.notes.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_other_user_delete_note(self):
        """Тестирование удаление заметки другим пользователем."""
        url = reverse('notes:delete', args=(self.notes.slug,))
        self.client.force_login(self.user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
