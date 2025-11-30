# Django Tree Menu

Тестовое задание — приложение древовидного меню на Django.

## Ключевые особенности

- **1 запрос к БД** на отрисовку каждого меню (ключевое требование)
- Меню через template tag: `{% draw_menu 'main_menu' %}`
- Редактирование через Django Admin
- Поддержка явных URL и named URL
- Автоматическое раскрытие пути к активному пункту

## Быстрый старт

```bash
# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Заполнение тестовыми данными
python manage.py populate_menu

# Создание суперпользователя
python create_superuser.py

# Запуск сервера
python manage.py runserver
```

## Демо

- **Сайт**: http://127.0.0.1:8000/
- **Админка**: http://127.0.0.1:8000/admin/ (admin / admin)

## Использование в шаблонах

```django
{% load menu_tags %}

{# Отрисовка меню по имени #}
{% draw_menu 'main_menu' %}
{% draw_menu 'footer_menu' %}
```

## Оптимизация: как достигается 1 запрос

```python
# ЕДИНСТВЕННЫЙ запрос - получаем все пункты меню
items = MenuItem.objects.filter(menu_name=menu_name)

# Строим дерево в Python (не в БД!)
items_dict = {item.id: item for item in items}
for item in items:
    if item.parent_id:
        items_dict[item.parent_id].children_list.append(item)
```

## Структура проекта

```
treemenu/
├── models.py          # Модель MenuItem
├── admin.py           # Конфигурация админки
├── templatetags/
│   └── menu_tags.py   # Template tag draw_menu
└── management/
    └── commands/
        └── populate_menu.py  # Команда заполнения БД
```

## Модель MenuItem

| Поле      | Описание                           |
|-----------|-----------------------------------|
| menu_name | Идентификатор меню (main_menu)    |
| title     | Отображаемое название             |
| parent    | FK на родительский пункт          |
| url       | Явный URL (/about/)               |
| named_url | Имя URL из urls.py (about)        |
| order     | Порядок сортировки                |

## Логика раскрытия меню

1. Всё над активным пунктом — развернуто
2. Первый уровень под активным — развернут
3. Остальное — свернуто

---

**Технологии**: Python 3.10+, Django 5.x
