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
