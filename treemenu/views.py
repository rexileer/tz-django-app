from django.views.generic import TemplateView


class DemoPageView(TemplateView):
    """
    Демо-страница для тестирования меню.
    Передаёт title для отображения текущей страницы.
    """
    template_name = 'demo.html'
    title = 'Главная'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context
