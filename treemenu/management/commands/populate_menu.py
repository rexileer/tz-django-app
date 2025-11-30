from django.core.management.base import BaseCommand
from treemenu.models import MenuItem


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми пунктами меню'

    def handle(self, *args, **options):
        # Очищаем старые данные
        MenuItem.objects.all().delete()
        
        # === ОСНОВНОЕ МЕНЮ (main_menu) ===
        
        # Корневые пункты
        home = MenuItem.objects.create(
            menu_name='main_menu',
            title='Главная',
            named_url='home',
            order=0
        )
        
        about = MenuItem.objects.create(
            menu_name='main_menu',
            title='О компании',
            named_url='about',
            order=1
        )
        
        services = MenuItem.objects.create(
            menu_name='main_menu',
            title='Услуги',
            named_url='services',
            order=2
        )
        
        contact = MenuItem.objects.create(
            menu_name='main_menu',
            title='Контакты',
            named_url='contact',
            order=3
        )
        
        # Подпункты "О компании"
        MenuItem.objects.create(
            menu_name='main_menu',
            title='Команда',
            parent=about,
            named_url='about_team',
            order=0
        )
        
        MenuItem.objects.create(
            menu_name='main_menu',
            title='История',
            parent=about,
            named_url='about_history',
            order=1
        )
        
        # Подпункты "Услуги"
        web = MenuItem.objects.create(
            menu_name='main_menu',
            title='Веб-разработка',
            parent=services,
            named_url='services_web',
            order=0
        )
        
        MenuItem.objects.create(
            menu_name='main_menu',
            title='Мобильные приложения',
            parent=services,
            named_url='services_mobile',
            order=1
        )
        
        MenuItem.objects.create(
            menu_name='main_menu',
            title='Дизайн',
            parent=services,
            named_url='services_design',
            order=2
        )
        
        # Глубокая вложенность для демонстрации
        MenuItem.objects.create(
            menu_name='main_menu',
            title='Frontend',
            parent=web,
            named_url='services_frontend',
            order=0
        )
        
        MenuItem.objects.create(
            menu_name='main_menu',
            title='Backend',
            parent=web,
            named_url='services_backend',
            order=1
        )
        
        # === ДОПОЛНИТЕЛЬНОЕ МЕНЮ (footer_menu) ===
        
        MenuItem.objects.create(
            menu_name='footer_menu',
            title='Политика конфиденциальности',
            named_url='privacy',
            order=0
        )
        
        MenuItem.objects.create(
            menu_name='footer_menu',
            title='Условия использования',
            named_url='terms',
            order=1
        )
        
        self.stdout.write(
            self.style.SUCCESS('Тестовые меню успешно созданы!')
        )
        self.stdout.write(
            f'  main_menu: {MenuItem.objects.filter(menu_name="main_menu").count()} пунктов'
        )
        self.stdout.write(
            f'  footer_menu: {MenuItem.objects.filter(menu_name="footer_menu").count()} пунктов'
        )

