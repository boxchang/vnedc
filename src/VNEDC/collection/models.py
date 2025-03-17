from django.db import models
from django.utils import timezone
from django.conf import settings

from users.models import Unit


class Plant(models.Model):
    plant_code = models.CharField(max_length=50, primary_key=True)
    plant_name = models.CharField(max_length=50)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='plant_update_by')

    def __str__(self):
        return self.plant_name


class Machine(models.Model):
    plant = models.ForeignKey(Plant, related_name='mach_plant', on_delete=models.CASCADE)
    mach_code = models.CharField(max_length=50, primary_key=True)
    mach_name = models.CharField(max_length=50)
    mold_type = models.CharField(max_length=50, null=True, blank=True)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='mach_update_by')

    def __str__(self):
        return self.mach_name


class Process_Type(models.Model):
    process_code = models.CharField(max_length=50, primary_key=True)
    process_name = models.CharField(max_length=50)  # 英文
    process_tw = models.CharField(max_length=50)  # 繁體中文
    process_cn = models.CharField(max_length=50)  # 簡體中文
    process_vn = models.CharField(max_length=50)  # 越語
    show_order = models.IntegerField(default=0)  # 排列順序
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='process_type_update_by')

    def __str__(self):
        from django.utils.translation import get_language
        lang = get_language()
        if lang == 'zh-hans':
            return self.process_cn
        elif lang == 'zh-hant':
            return self.process_tw
        elif lang == 'vi':
            return self.process_vn
        return self.process_name


class Parameter_Type(models.Model):
    process_type = models.ForeignKey(Process_Type, related_name='param_type_process_type', on_delete=models.CASCADE, null=True, blank=True)
    param_type_code = models.CharField(max_length=50)
    control_table = models.CharField(max_length=50, null=True, blank=True)
    control_high_column = models.CharField(max_length=50, null=True, blank=True)
    control_low_column = models.CharField(max_length=50, null=True, blank=True)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='param_type_update_by')

    def __str__(self):
        return str(self.process_type.process_code) + "_" + str(self.param_code)


class ParameterDefine(models.Model):
    plant = models.ForeignKey(Plant, related_name='param_plant', on_delete=models.CASCADE)
    mach = models.ForeignKey(Machine, related_name='param_mach', on_delete=models.CASCADE)
    process_type = models.ForeignKey(Process_Type, related_name='param_process_type', on_delete=models.CASCADE)
    param_type = models.CharField(max_length=50, null=True, blank=True)
    side = models.CharField(max_length=5, null=True, blank=True)
    parameter_name = models.CharField(max_length=50)  # 英文
    parameter_tw = models.CharField(max_length=50)  # 繁體中文
    parameter_cn = models.CharField(max_length=50)  # 簡體中文
    parameter_vn = models.CharField(max_length=50)  # 越語
    show_order = models.IntegerField(default=0)  # 排列順序
    unit = models.CharField(max_length=50, null=True, blank=True)
    control_range_low = models.FloatField(null=True, blank=True)
    base_line = models.FloatField(null=True, blank=True)
    control_range_high = models.FloatField(null=True, blank=True)
    sampling_frequency = models.CharField(max_length=50, null=True, blank=True)
    input_time = models.CharField(max_length=50, null=True, blank=True)
    auto_value = models.BooleanField(default=False)
    scada_table = models.CharField(max_length=50, null=True, blank=True)
    scada_column = models.CharField(max_length=50, null=True, blank=True)
    text_color = models.CharField(max_length=50, null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now, null=True)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='param_define_create_by', null=True)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='param_define_update_by')
    pda_value = models.BooleanField(default=False)

    def __str__(self):
        from django.utils.translation import get_language
        lang = get_language()
        if lang == 'zh-hans':
            return self.parameter_cn
        elif lang == 'zh-hant':
            return self.parameter_tw
        elif lang == 'vi':
            return self.parameter_vn
        return self.parameter_name


class ParameterValue(models.Model):
    data_date = models.DateField()
    plant = models.ForeignKey(Plant, related_name='param_value_plant', on_delete=models.CASCADE)
    mach = models.ForeignKey(Machine, related_name='param_value_mach', on_delete=models.CASCADE)
    process_type = models.CharField(max_length=50)
    data_time = models.CharField(max_length=50)
    parameter_name = models.CharField(max_length=50)  # 英文
    parameter_value = models.FloatField(null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='param_value_create_by')
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='param_value_update_by')


class Daily_Prod_Info(models.Model):
    data_date = models.DateField()
    plant = models.ForeignKey(Plant, related_name='daily_info_plant', on_delete=models.CASCADE)
    mach = models.ForeignKey(Machine, related_name='daily_info_mach', on_delete=models.CASCADE)
    prod_name_a1 = models.CharField(max_length=100, null=True, blank=True)
    prod_size_a1 = models.CharField(max_length=50, null=True, blank=True)
    prod_name_a2 = models.CharField(max_length=100, null=True, blank=True)
    prod_size_a2 = models.CharField(max_length=50, null=True, blank=True)
    prod_name_b1 = models.CharField(max_length=100, null=True, blank=True)
    prod_size_b1 = models.CharField(max_length=50, null=True, blank=True)
    prod_name_b2 = models.CharField(max_length=100, null=True, blank=True)
    prod_size_b2 = models.CharField(max_length=50, null=True, blank=True)
    coagulant_time_hour = models.CharField(max_length=50, null=True, blank=True)
    coagulant_time_min = models.CharField(max_length=50, null=True, blank=True)
    latex_time_hour = models.CharField(max_length=50, null=True, blank=True)
    latex_time_min = models.CharField(max_length=50, null=True, blank=True)
    tooling_time_hour = models.CharField(max_length=50, null=True, blank=True)
    tooling_time_min = models.CharField(max_length=50, null=True, blank=True)
    remark = models.CharField(max_length=50, null=True, blank=True)
    remark2 = models.CharField(max_length=500, null=True, blank=True)
    handmold_brand = models.CharField(max_length=50, null=True, blank=True)
    handmold_spec = models.CharField(max_length=50, null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='daily_info_create_by')
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='daily_info_update_by')


class Daily_Prod_Info_Head(models.Model):
    data_date = models.DateField()
    plant = models.ForeignKey(Plant, related_name='daily_info_head_plant', on_delete=models.CASCADE, null=True, blank=True)
    mach = models.ForeignKey(Machine, related_name='daily_info_head_mach', on_delete=models.CASCADE, null=True, blank=True)
    line = models.CharField(max_length=50)
    product = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='daily_info_head_create_by')


class Lab_Parameter_Control(models.Model):
    plant = models.ForeignKey(Plant, related_name='lab_param_plant', on_delete=models.CASCADE)
    mach = models.ForeignKey(Machine, related_name='lab_param_mach', on_delete=models.CASCADE)
    item_no = models.CharField(max_length=50)
    process_type = models.CharField(max_length=50)
    parameter_name = models.CharField(max_length=50)
    control_range_low = models.FloatField(null=True, blank=True)
    base_line = models.FloatField(null=True, blank=True)
    control_range_high = models.FloatField(null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now, null=True)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='lab_param_create_by', null=True)


