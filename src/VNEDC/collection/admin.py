from django.contrib import admin
from collection.models import ParameterDefine, Process_Type, Plant, Machine


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('plant_code', 'plant_name', 'update_at', 'update_by')


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('plant', 'mach_code', 'mach_name', 'update_at', 'update_by')


@admin.register(Process_Type)
class Process_TypeAdmin(admin.ModelAdmin):
    list_display = ('process_code', 'process_name', 'process_tw', 'update_at', 'update_by')



@admin.register(ParameterDefine)
class ParameterDefineAdmin(admin.ModelAdmin):
    list_display = ('plant', 'mach', 'process_type', 'parameter_name', 'parameter_tw', 'parameter_cn', 'parameter_vn', 'show_order')

