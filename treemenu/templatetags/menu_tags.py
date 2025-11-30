from django import template
from django.utils.safestring import mark_safe
from treemenu.models import MenuItem

register = template.Library()


def build_tree(items):
    """
    Строит дерево из плоского списка элементов.
    Возвращает (items_dict, root_items).
    
    ВАЖНО: Это ключевая оптимизация - строим дерево в Python,
    а не делаем N+1 запросов к БД.
    """
    items_dict = {}
    root_items = []
    
    # Первый проход: индексируем все элементы
    for item in items:
        item.children_list = []  # Динамический атрибут для детей
        items_dict[item.id] = item
    
    # Второй проход: связываем родителей с детьми
    for item in items:
        if item.parent_id:
            parent = items_dict.get(item.parent_id)
            if parent:
                parent.children_list.append(item)
        else:
            root_items.append(item)
    
    return items_dict, root_items


def get_active_path(items_dict, current_url):
    """
    Находит активный элемент и строит путь от него к корню.
    Возвращает (active_id, path_set).
    """
    active_id = None
    path = set()
    
    # Ищем элемент с совпадающим URL
    for item_id, item in items_dict.items():
        item_url = item.get_url()
        if item_url and item_url != '#' and current_url == item_url:
            active_id = item_id
            # Строим путь вверх до корня
            node = item
            while node:
                path.add(node.id)
                node = items_dict.get(node.parent_id)
            break
    
    return active_id, path


def render_menu_items(items, active_id, active_path, items_dict):
    """
    Рендерит список пунктов меню в HTML.
    
    Логика раскрытия:
    - Пункт раскрыт если он в active_path (сам активный или его предок)
    - Также раскрыт первый уровень под активным пунктом
    """
    if not items:
        return ''
    
    html = ['<ul class="tree-menu">']
    
    for item in items:
        is_active = item.id == active_id
        is_in_path = item.id in active_path
        
        # Определяем, нужно ли раскрыть детей
        # 1) Если пункт в пути к активному - раскрываем
        # 2) Если родитель этого пункта активный - раскрываем (первый уровень под активным)
        parent_is_active = item.parent_id and item.parent_id == active_id
        should_expand = is_in_path or parent_is_active
        
        # CSS классы
        classes = []
        if is_active:
            classes.append('active')
        if is_in_path:
            classes.append('in-path')
        if item.children_list:
            classes.append('has-children')
            if should_expand:
                classes.append('expanded')
        
        class_str = f' class="{" ".join(classes)}"' if classes else ''
        
        html.append(f'<li{class_str}>')
        html.append(f'<a href="{item.get_url()}">{item.title}</a>')
        
        # Рекурсивно рендерим детей если нужно раскрыть
        if item.children_list and should_expand:
            html.append(render_menu_items(
                item.children_list, active_id, active_path, items_dict
            ))
        
        html.append('</li>')
    
    html.append('</ul>')
    return ''.join(html)


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Template tag для отрисовки меню.
    
    Использование: {% draw_menu 'main_menu' %}
    
    ГАРАНТИЯ: Ровно 1 запрос к БД на одно меню.
    """
    request = context.get('request')
    current_url = request.path if request else ''
    
    # === ЕДИНСТВЕННЫЙ ЗАПРОС К БД ===
    items = list(MenuItem.objects.filter(menu_name=menu_name))
    
    if not items:
        return ''
    
    # Строим дерево в памяти
    items_dict, root_items = build_tree(items)
    
    # Находим активный путь
    active_id, active_path = get_active_path(items_dict, current_url)
    
    # Рендерим HTML
    html = render_menu_items(root_items, active_id, active_path, items_dict)
    
    return mark_safe(html)



