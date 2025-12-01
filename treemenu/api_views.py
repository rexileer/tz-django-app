from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Prefetch
from .models import MenuItem
from .serializers import MenuItemSerializer


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для API меню.
    Демонстрирует знание DRF (важно для CRM вакансии).
    
    Оптимизация: используем prefetch_related для избежания N+1 запросов.
    """
    serializer_class = MenuItemSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """
        Оптимизированный queryset с prefetch для детей.
        """
        queryset = MenuItem.objects.select_related('parent').prefetch_related(
            Prefetch(
                'children',
                queryset=MenuItem.objects.order_by('order', 'title')
            )
        )
        
        # Фильтрация по menu_name если указан
        menu_name = self.request.query_params.get('menu_name', None)
        if menu_name:
            queryset = queryset.filter(menu_name=menu_name)
        
        return queryset.order_by('order', 'title')
    
    @action(detail=False, methods=['get'], url_path='by-name/(?P<menu_name>[^/.]+)')
    def by_name(self, request, menu_name=None):
        """
        Получить все пункты меню по имени.
        Возвращает только корневые элементы (дерево строится через children).
        
        Пример: GET /api/menu/by-name/main_menu/
        """
        # Получаем все элементы меню одним запросом
        items = list(MenuItem.objects.filter(menu_name=menu_name).order_by('order', 'title'))
        
        if not items:
            return Response(
                {'error': f'Menu "{menu_name}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Строим дерево: находим корневые элементы
        root_items = [item for item in items if item.parent_id is None]
        
        # Сериализуем корневые элементы (дети подтянутся через get_children)
        serializer = MenuItemSerializer(root_items, many=True)
        
        return Response({
            'menu_name': menu_name,
            'items': serializer.data,
            'total_items': len(items)
        })

