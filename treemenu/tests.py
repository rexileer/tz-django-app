from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from treemenu.models import MenuItem


class MenuItemModelTest(TestCase):
    """Тесты модели MenuItem"""
    
    def setUp(self):
        self.menu_name = 'test_menu'
        self.root = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Root',
            order=0
        )
    
    def test_create_menu_item(self):
        """Тест создания пункта меню"""
        item = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Test Item',
            parent=self.root,
            order=1
        )
        self.assertEqual(item.title, 'Test Item')
        self.assertEqual(item.parent, self.root)
        self.assertIn(item, self.root.children.all())
    
    def test_get_url_named_url(self):
        """Тест получения URL через named_url"""
        item = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Home',
            named_url='home',
            order=0
        )
        # Проверяем что метод не падает
        url = item.get_url()
        self.assertIsInstance(url, str)
    
    def test_get_url_explicit_url(self):
        """Тест получения явного URL"""
        item = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='About',
            url='/about/',
            order=0
        )
        self.assertEqual(item.get_url(), '/about/')
    
    def test_get_url_fallback(self):
        """Тест fallback на '#' если URL не задан"""
        item = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='No URL',
            order=0
        )
        self.assertEqual(item.get_url(), '#')
    
    def test_tree_structure(self):
        """Тест древовидной структуры"""
        child1 = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Child 1',
            parent=self.root,
            order=0
        )
        child2 = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Child 2',
            parent=self.root,
            order=1
        )
        
        self.assertEqual(self.root.children.count(), 2)
        self.assertIn(child1, self.root.children.all())
        self.assertIn(child2, self.root.children.all())
    
    def test_cascade_delete(self):
        """Тест каскадного удаления"""
        child = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Child',
            parent=self.root,
            order=0
        )
        child_id = child.id
        
        self.root.delete()
        # Дети должны удалиться каскадно
        self.assertFalse(MenuItem.objects.filter(id=child_id).exists())


class MenuTemplateTagTest(TestCase):
    """Тесты template tag draw_menu"""
    
    def setUp(self):
        self.client = Client()
        # Создаём тестовое меню
        self.root = MenuItem.objects.create(
            menu_name='test_menu',
            title='Root',
            named_url='home',
            order=0
        )
        self.child = MenuItem.objects.create(
            menu_name='test_menu',
            title='Child',
            parent=self.root,
            url='/child/',
            order=0
        )
    
    def test_draw_menu_empty(self):
        """Тест отрисовки несуществующего меню"""
        from treemenu.templatetags.menu_tags import draw_menu
        from django.template import Context, Template
        
        template = Template('{% load menu_tags %}{% draw_menu "nonexistent" %}')
        context = Context({'request': None})
        result = template.render(context)
        
        self.assertEqual(result.strip(), '')
    
    def test_draw_menu_renders(self):
        """Тест что меню рендерится"""
        from treemenu.templatetags.menu_tags import draw_menu
        from django.template import Context, Template
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        
        template = Template('{% load menu_tags %}{% draw_menu "test_menu" %}')
        context = Context({'request': request})
        result = template.render(context)
        
        self.assertIn('Root', result)
        self.assertIn('Child', result)
        self.assertIn('tree-menu', result)


class MenuAPITest(TestCase):
    """Тесты DRF API"""
    
    def setUp(self):
        self.client = Client()
        self.root = MenuItem.objects.create(
            menu_name='api_menu',
            title='Root',
            order=0
        )
    
    def test_api_list_menu_items(self):
        """Тест получения списка пунктов меню через API"""
        response = self.client.get('/api/menu/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json() or response.json())
    
    def test_api_get_menu_by_name(self):
        """Тест получения меню по имени через API"""
        response = self.client.get('/api/menu/by-name/api_menu/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['menu_name'], 'api_menu')
        self.assertIn('items', data)
    
    def test_api_get_nonexistent_menu(self):
        """Тест получения несуществующего меню"""
        response = self.client.get('/api/menu/by-name/nonexistent/')
        self.assertEqual(response.status_code, 404)


class MenuOptimizationTest(TestCase):
    """Тесты оптимизации - проверка количества запросов"""
    
    def setUp(self):
        # Создаём меню с несколькими уровнями
        self.menu_name = 'perf_test'
        root = MenuItem.objects.create(
            menu_name=self.menu_name,
            title='Root',
            order=0
        )
        
        # Создаём 10 детей первого уровня
        for i in range(10):
            child = MenuItem.objects.create(
                menu_name=self.menu_name,
                title=f'Child {i}',
                parent=root,
                order=i
            )
            # У каждого ребёнка по 5 внуков
            for j in range(5):
                MenuItem.objects.create(
                    menu_name=self.menu_name,
                    title=f'Grandchild {i}-{j}',
                    parent=child,
                    order=j
                )
    
    def test_single_query_for_menu(self):
        """
        Тест что для меню делается только 1 запрос к БД.
        
        ВАЖНО: Это ключевая оптимизация проекта.
        Вместо N+1 запросов (по одному на каждый уровень дерева),
        мы делаем 1 запрос и строим дерево в памяти.
        """
        from django.template import Context, Template
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/')
        
        template = Template('{% load menu_tags %}{% draw_menu "perf_test" %}')
        context = Context({'request': request})
        
        # Подсчитываем запросы - должен быть 1 SELECT для MenuItem
        # (могут быть дополнительные запросы для других таблиц Django)
        with self.assertNumQueries(1, using='default'):
            result = template.render(context)
            self.assertIsNotNone(result)
            self.assertIn('Root', result)
