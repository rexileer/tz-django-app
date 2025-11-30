from django.urls import path
from .views import DemoPageView

urlpatterns = [
    path('', DemoPageView.as_view(title='Главная'), name='home'),
    path('about/', DemoPageView.as_view(title='О компании'), name='about'),
    path('about/team/', DemoPageView.as_view(title='Команда'), name='about_team'),
    path('about/history/', DemoPageView.as_view(title='История'), name='about_history'),
    path('services/', DemoPageView.as_view(title='Услуги'), name='services'),
    path('services/web/', DemoPageView.as_view(title='Веб-разработка'), name='services_web'),
    path('services/web/frontend/', DemoPageView.as_view(title='Frontend'), name='services_frontend'),
    path('services/web/backend/', DemoPageView.as_view(title='Backend'), name='services_backend'),
    path('services/mobile/', DemoPageView.as_view(title='Мобильные приложения'), name='services_mobile'),
    path('services/design/', DemoPageView.as_view(title='Дизайн'), name='services_design'),
    path('contact/', DemoPageView.as_view(title='Контакты'), name='contact'),
    path('privacy/', DemoPageView.as_view(title='Политика конфиденциальности'), name='privacy'),
    path('terms/', DemoPageView.as_view(title='Условия использования'), name='terms'),
]

