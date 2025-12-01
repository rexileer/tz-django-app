from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Админка для управления пунктами меню.
    """
    list_display = ('title', 'menu_name', 'parent', 'url', 'named_url', 'order', 'has_children')
    list_filter = ('menu_name',)
    list_editable = ('order',)
    search_fields = ('title', 'url', 'named_url', 'menu_name')
    ordering = ('menu_name', 'order', 'title')
    readonly_fields = ('id',)
    
    fieldsets = (
        (None, {
            'fields': ('menu_name', 'title', 'parent', 'order')
        }),
        ('URL настройки', {
            'fields': ('url', 'named_url'),
            'description': 'Укажите либо явный URL, либо named URL (из urls.py). '
                          'Если указаны оба, приоритет у named_url.'
        }),
    )
    
    def has_children(self, obj):
        """Показывает есть ли у пункта дети"""
        return obj.children.exists()
    has_children.boolean = True
    has_children.short_description = 'Есть дети'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Фильтруем выбор родителя - показываем только пункты того же меню.
        Это предотвращает ошибки при создании дерева.
        """
        if db_field.name == 'parent':
            # При редактировании существующего объекта
            if request.resolver_match.kwargs.get('object_id'):
                obj_id = request.resolver_match.kwargs['object_id']
                try:
                    obj = MenuItem.objects.get(pk=obj_id)
                    # Показываем только пункты из того же меню, исключая сам объект
                    kwargs['queryset'] = MenuItem.objects.filter(
                        menu_name=obj.menu_name
                    ).exclude(pk=obj_id)
                except MenuItem.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
