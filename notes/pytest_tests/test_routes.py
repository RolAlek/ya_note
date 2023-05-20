from http import HTTPStatus
import pytest

from django.shortcuts import reverse
from pytest_django.asserts import assertRedirects

# План тестирования:
# 1. Главная страница доступна анонимному пользователю.

# 2. Аутентифицированному пользователю доступна страница со списком заметок
# notes/, страница успешного добавления заметки done/, страница добавления
# новой заметки add/.

# 3. Страницы отдельной заметки, удаления и редактирования заметки доступны
# только автору заметки. Если на эти страницы попытается зайти другой
# пользователь — вернётся ошибка 404.

# 4. При попытке перейти на страницу списка заметок, страницу успешного
# добавления записи, страницу добавления заметки, отдельной заметки,
# редактирования или удаления заметки анонимный пользователь перенаправляется
# на страницу логина.

# 5. Страницы регистрации пользователей, входа в учётную запись и выхода из
# неё доступны всем пользователям.


@pytest.mark.parametrize(
    'name',
    ('notes:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    """Тест доступности домашней страници и страниц
    управления пользователем. (1, 5)
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('notes:list', 'notes:add', 'notes:success')
)
def test_pages_availability_for_auth_user(admin_client, name):
    """Тест доступности страниц предназначенных
    для авторизованного пользователя. (2)
    """
    url = reverse(name)
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args'))
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, args, expected_status
):
    """Страницы отдельной заметки, удаления и редактирования заметки доступны
    только автору заметки. (3)
    """
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('notes:detail', pytest.lazy_fixture('slug_for_args')),
        ('notes:edit', pytest.lazy_fixture('slug_for_args')),
        ('notes:delete', pytest.lazy_fixture('slug_for_args')),
        ('notes:add', None),
        ('notes:success', None),
        ('notes:list', None)
    ),
)
def test_redirects(client, name, args):
    """Тестирование перенаправления анонимного пользователя на страницу
    авторизации. (4)
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
