from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


class Warehouse(models.Model):
    wh_code = models.CharField(primary_key=True, max_length=20)  # Primary key with varchar(20)
    wh_name = models.CharField(max_length=100)  # Name with varchar(100)
    wh_comment = models.CharField(max_length=500, null=True, blank=True)  # Comment, nullable
    wh_bg = models.ImageField(upload_to='warehouse_images/', null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)  # Creation timestamp
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='warehouse_create_by')
    update_at = models.DateTimeField(default=timezone.now)  # Last updated timestamp
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='warehouse_update_by')

    def save(self, *args, **kwargs):
        # Lấy người dùng từ kwargs hoặc từ session nếu không truyền trực tiếp
        user = kwargs.pop('user', None)

        if not self.pk:  # Nếu là bản ghi mới
            if user:
                self.create_by = user  # Gán người dùng vào create_by
                self.create_at = timezone.now()  # Gán thời gian tạo
            else:
                raise ValueError("User must be provided for 'create_by'.")  # Nếu không có người dùng, raise lỗi

        if user:
            self.update_by = user  # Gán người dùng vào update_by
        self.update_at = timezone.now()  # Cập nhật thời gian update

        super().save(*args, **kwargs)  # Gọi phương thức save của lớp cha

    def __str__(self):
        return self.wh_code  # Human-readable string representation


class Area(models.Model):
    area_id = models.CharField(max_length=20, unique=True, primary_key=True)
    area_name = models.CharField(max_length=100)
    warehouse = models.ForeignKey(Warehouse, related_name='area_warehouse', on_delete=models.CASCADE)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='area_create_by')
    update_at = models.DateTimeField(default=timezone.now)  # Tự động cập nhật thời gian mỗi khi bản ghi được cập nhật
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='area_update_by')

    def save(self, *args, **kwargs):
        # Lấy người dùng từ kwargs hoặc từ session nếu không truyền trực tiếp
        user = kwargs.pop('user', None)

        if not self.pk:  # Nếu là bản ghi mới
            if user:
                self.create_by = user  # Gán người dùng vào create_by
                self.create_at = timezone.now()  # Gán thời gian tạo
            else:
                raise ValueError("User must be provided for 'create_by'.")  # Nếu không có người dùng, raise lỗi

        if user:
            self.update_by = user  # Gán người dùng vào update_by
        self.update_at = timezone.now()  # Cập nhật thời gian update

        super().save(*args, **kwargs)  # Gọi phương thức save của lớp cha

    def __str__(self):
        return self.area_id


class Bin(models.Model):
    bin_id = models.CharField(max_length=20, unique=True, primary_key=True)
    bin_name = models.CharField(max_length=100)
    area = models.ForeignKey(Area, related_name='bin_area', on_delete=models.CASCADE)  # Liên kết với bảng Area
    pos_x = models.IntegerField(blank=True, null=True)  # Toạ độ X, có thể null
    pos_y = models.IntegerField(blank=True, null=True)  # Toạ độ Y, có thể null
    bin_w = models.IntegerField(blank=True, null=True)  # Bin Width
    bin_l = models.IntegerField(blank=True, null=True)  # Bin Length
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='bin_create_by')
    update_at = models.DateTimeField(default=timezone.now)  # Tự động cập nhật thời gian mỗi khi bản ghi được cập nhật
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='bin_update_by')

    def save(self, *args, **kwargs):
        # Lấy người dùng từ kwargs hoặc từ session nếu không truyền trực tiếp
        user = kwargs.pop('user', None)

        if not self.pk:  # Nếu là bản ghi mới
            if user:
                self.create_by = user  # Gán người dùng vào create_by
                self.create_at = timezone.now()  # Gán thời gian tạo
            else:
                raise ValueError("User must be provided for 'create_by'.")  # Nếu không có người dùng, raise lỗi

        if user:
            self.update_by = user  # Gán người dùng vào update_by
        self.update_at = timezone.now()  # Cập nhật thời gian update

        super().save(*args, **kwargs)  # Gọi phương thức save của lớp cha

    def __str__(self):
        return self.bin_id


class Attribute(models.Model):
    attr_id = models.CharField(max_length=20, unique=True, primary_key=True)
    attr_name = models.CharField(max_length=50)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='attr_update_by')


class Area_Attribute(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='area_attr_update_by')


class Bin_Attr_Value(models.Model):
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='bin_attr_value_create_by')


class MovementType(models.Model):
    mvt_code = models.CharField(max_length=20, primary_key=True)
    mvt_name = models.CharField(max_length=20, blank=False, null=False)
    desc = models.CharField(max_length=200, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, editable=True)  # 建立日期
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='mvt_create_by')  # 建立者

    def __str__(self):
        return self.mvt_code


class Bin_Value(models.Model):
    bin = models.ForeignKey(Bin, related_name='value_bin', on_delete=models.CASCADE)
    product_order = models.CharField(max_length=50, null=False, blank=False)
    purchase_no = models.CharField(max_length=50, null=True, blank=True)
    version_no = models.CharField(max_length=50, null=True, blank=True)
    version_seq = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=5, null=False, blank=False)
    qty = models.IntegerField(blank=True, null=True)
    purchase_unit = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=5, null=False, blank=False)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='bin_value_update_by')

    def __str__(self):
        return self.bin.bin_id
    #     return self.bin.bin_id
        # return f"Bin: {self.bin} - PO: {self.product_order} - PN: {self.purchase_no} - VN: {self.version_no} - " \
        #        f"VS: {self.version_seq}"


class Bin_Value_History(models.Model):
    batch_no = models.CharField(max_length=50, null=False, blank=False)
    bin = models.ForeignKey('Bin', related_name='value_hist_bin', on_delete=models.CASCADE)
    product_order = models.CharField(max_length=50, null=False, blank=False)  # PO
    purchase_no = models.CharField(max_length=50, null=True, blank=True)
    version_no = models.CharField(max_length=50, null=True, blank=True)
    version_seq = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=5, null=False, blank=False)  # Size
    mvt = models.ForeignKey('MovementType', related_name='stockin_hist_mvt', on_delete=models.DO_NOTHING)  # Type (STOCKIN / STOCKOUT)
    plus_qty = models.IntegerField()
    minus_qty = models.IntegerField()
    remain_qty = models.IntegerField()
    purchase_unit = models.CharField(max_length=20, blank=True, null=True)
    comment = models.CharField(max_length=200, null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)  # Create_at
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='bin_value_hist_create_by'
    )  # Create_by


class ItemType(models.Model):
    type_code = models.CharField(max_length=20, primary_key=True)
    type_name = models.CharField(max_length=20, blank=False, null=False)
    desc = models.CharField(max_length=200, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, editable=True)  # 建立日期
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='itemtype_create_by')  # 建立者

    def __str__(self):
        return self.desc


class UnitType(models.Model):
    unit_code = models.CharField(max_length=20, primary_key=True)
    unit_name = models.CharField(max_length=20, blank=False, null=False)
    desc = models.CharField(max_length=200, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, editable=True)  # 建立日期
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='unittype_create_by')  # 建立者

    def __str__(self):
        return self.desc


class PackMethod(models.Model):
    pack_code = models.CharField(max_length=20, primary_key=True)
    pack_name = models.CharField(max_length=20, blank=False, null=False)
    desc = models.CharField(max_length=200, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, editable=True)  # 建立日期
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='packmethod_create_by')  # 建立者

    def __str__(self):
        return self.desc


class StockInForm(models.Model):
    form_no = models.CharField(max_length=20, primary_key=True)
    create_at = models.DateTimeField(auto_now_add=True, editable=True)  # 建立日期
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='stockin_form_create_by')  # 建立者

    def get_absolute_url(self):
        return reverse('stockin_detail', kwargs={'pk': self.pk})


class StockInFormDetail(models.Model):
    form_no = models.ForeignKey('StockInForm', related_name='stockin_detail_form', on_delete=models.CASCADE)
    product_order = models.CharField(max_length=20, blank=True, null=True)
    customer_no = models.CharField(max_length=20, blank=True, null=True)
    version_no = models.CharField(max_length=20, blank=True, null=True)
    version_seq = models.CharField(max_length=20, blank=True, null=True)
    lot_no = models.CharField(max_length=20, blank=True, null=True)
    item_type = models.ForeignKey('ItemType', related_name='stockin_itemtype', on_delete=models.DO_NOTHING)
    packing_type = models.CharField(max_length=20, blank=True, null=True)
    purchase_no = models.CharField(max_length=20, blank=True, null=True)
    purchase_qty = models.IntegerField(default=0, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    purchase_unit = models.CharField(max_length=20, blank=True, null=True)
    post_date = models.CharField(max_length=20, blank=True, null=True)
    order_qty = models.IntegerField(default=0, blank=True, null=True)
    order_bin = models.ForeignKey('Bin', related_name='stockin_order_bin', on_delete=models.DO_NOTHING)
    supplier = models.CharField(max_length=20, blank=True, null=True)
    sap_mtr_no = models.CharField(max_length=20, blank=True, null=True)
    desc = models.CharField(max_length=2000, blank=True, null=True)


class StockOutForm(models.Model):
    form_no = models.CharField(max_length=20, primary_key=True)
    create_at = models.DateTimeField(auto_now_add=True, editable=True)  # 建立日期
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='stockout_form_create_by')  # 建立者


class StockOutFormDetail(models.Model):
    form_no = models.ForeignKey('StockOutForm', related_name='stockout_detail_form', on_delete=models.CASCADE)
    product_order = models.CharField(max_length=20, blank=True, null=True)
    version_no = models.CharField(max_length=20, blank=True, null=True)
    version_seq = models.CharField(max_length=20, blank=True, null=True)
    purchase_no = models.CharField(max_length=20, blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    purchase_unit = models.CharField(max_length=20, blank=False, null=True)
    order_bin = models.ForeignKey('Bin', related_name='stockout_order_bin', on_delete=models.DO_NOTHING)
    desc = models.CharField(max_length=2000, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('stockout_detail', kwargs={'pk': self.pk})


class Series(models.Model):
    key = models.CharField(max_length=50, blank=False, null=False)
    series = models.IntegerField()
    desc = models.CharField(max_length=50, blank=True, null=True)