from rest_framework import serializers
from .models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """
    Serializer для MenuItem.
    Показывает знание DRF (важно для CRM вакансии).
    """
    children = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'menu_name', 'parent', 'url', 'named_url', 'order', 'children']
        read_only_fields = ['id']
    
    def get_children(self, obj):
        """Рекурсивно сериализуем детей"""
        children = obj.children.all().order_by('order', 'title')
        return MenuItemSerializer(children, many=True).data
    
    def get_url(self, obj):
        """Возвращаем вычисленный URL"""
        return obj.get_url()


class MenuListSerializer(serializers.Serializer):
    """
    Serializer для списка меню по имени.
    Используется в API endpoint.
    """
    menu_name = serializers.CharField(max_length=50)
    items = MenuItemSerializer(many=True, read_only=True)


