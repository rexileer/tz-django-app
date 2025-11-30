from django.contrib import admin
from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Админка для управления пунктами меню.
    """
    list_display = ('title', 'menu_name', 'parent', 'url', 'named_url', 'order')
    list_filter = ('menu_name',)
    list_editable = ('order',)
    search_fields = ('title', 'url', 'named_url')
    ordering = ('menu_name', 'order', 'title')
    
    # Группировка полей в форме
    fieldsets = (
        (None, {
            'fields': ('menu_name', 'title', 'parent', 'order')
        }),
        ('URL настройки', {
            'fields': ('url', 'named_url'),
            'description': 'Укажите либо явный URL, либо named URL (из urls.py)'
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Фильтруем выбор родителя - показываем только пункты того же меню.
        """
        if db_field.name == 'parent':
            # Получаем menu_name из текущего объекта, если редактируем
            if request.resolver_match.kwargs.get('object_id'):
                obj_id = request.resolver_match.kwargs['object_id']
                try:
                    obj = MenuItem.objects.get(pk=obj_id)
                    kwargs['queryset'] = MenuItem.objects.filter(
                        menu_name=obj.menu_name
                    ).exclude(pk=obj_id)
                except MenuItem.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
