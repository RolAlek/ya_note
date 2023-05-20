import pytest

from django.shortcuts import reverse

# План тестирования:
# 1. Отдельная заметка передаётся на страницу со списком заметок в списке
# object_list, в словаре context;

# 2. В список заметок одного пользователя не попадают заметки другого
# пользователя;

# 3. На страницы создания и редактирования заметки передаются формы.


@pytest.mark.parametrize(
        'paramitraized_client, note_in_list',
        (
            (pytest.lazy_fixture('author_client'), True),
            (pytest.lazy_fixture('admin_client'), False)
        ),
)
def test_note_list_for_different_user(
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
