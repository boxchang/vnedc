from django.contrib import admin
from warehouse.models import MovementType, ItemType, Warehouse, Plant


@admin.register(MovementType)
class MovementTypeAdmin(admin.ModelAdmin):
    list_display = ('mvt_code', 'mvt_name', 'desc')


@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('type_code', 'type_name', 'desc')


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('plant_code', 'plant_name')