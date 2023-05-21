import pytest

from django.shortcuts import reverse


@pytest.mark.parametrize(
        'paramitraized_client, note_in_list',
        (
            (pytest.lazy_fixture('author_client'), True),
            (pytest.lazy_fixture('admin_client'), False)
        ),
)
def test_note_in_list_for_different_user(
    note, paramitraized_client, note_in_list
):
    """
    Тестирование наличия заметки на странице списка заметок автора и что
    заметки одного пользователя не попадают на страницу списка друго
    пользователя. (1, 2)
    """
    url = reverse('notes:list')
    response = paramitraized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


@pytest.mark.parametrize(
        'name, args',
        (
            ('notes:add', None),
            ('notes:edit', pytest.lazy_fixture('slug_for_args'))
        ),
)
def test_pages_contains_form(name, args, author_client):
    """
    Тестирование наличия формы на страницах создания и редактирования заметки.
    """
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
