from django.db import models
from django.utils import timezone
from django.conf import settings

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

class Bin_Value(models.Model):
    bin = models.ForeignKey(Bin, related_name='value_bin', on_delete=models.CASCADE)
    po_no = models.CharField(max_length=50, null=False, blank=False)
    size = models.CharField(max_length=5, null=False, blank=False)
    qty = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=5, null=False, blank=False)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                  related_name='bin_value_update_by')

class Bin_Value_History(models.Model):
    bin = models.ForeignKey('Bin', related_name='value_hist_bin', on_delete=models.CASCADE)
    po_no = models.CharField(max_length=50, null=False, blank=False)  # PO
    size = models.CharField(max_length=5, null=False, blank=False)  # Size
    act_type = models.CharField(max_length=10, null=False, blank=False)  # Type (STOCKIN / STOCKOUT)
    old_qty = models.IntegerField()  # Old Qty
    act_qty = models.IntegerField()  # Action (+/- qty)
    new_qty = models.IntegerField()  # New Qty
    create_at = models.DateTimeField(default=timezone.now)  # Create_at
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='bin_value_hist_create_by'
    )  # Create_by
