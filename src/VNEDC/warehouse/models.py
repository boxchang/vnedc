from django.db import models
from django.utils import timezone

class Warehouse(models.Model):
    wh_code = models.CharField(primary_key=True, max_length=20)  # Primary key with varchar(20)
    wh_name = models.CharField(max_length=100)  # Name with varchar(100)
    wh_comment = models.CharField(max_length=500, null=True, blank=True)  # Comment, nullable
    wh_bg = models.ImageField(upload_to='warehouse_images/', null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)  # Creation timestamp
    create_by = models.CharField(max_length=50, null=True, blank=True)  # Created by, nullable
    update_at = models.DateTimeField(default=timezone.now)  # Last updated timestamp
    update_by = models.CharField(max_length=50, null=True, blank=True)  # Updated by, nullable

    def save(self, *args, **kwargs):
        # Chỉ cập nhật `update_at` nếu không phải là bản ghi mới
        if self.pk:  # Kiểm tra nếu tồn tại khóa chính
            self.update_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.wh_code  # Human-readable string representation


class Area(models.Model):
    area_id = models.CharField(max_length=20, unique=True, primary_key=True)
    area_name = models.CharField(max_length=100)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.CharField(max_length=100, null=True)  # Lưu tên hoặc ID người tạo
    update_at = models.DateTimeField(default=timezone.now)  # Tự động cập nhật thời gian mỗi khi bản ghi được cập nhật
    update_by = models.CharField(max_length=100, null=True)  # Lưu tên hoặc ID người cập nhật

    def __str__(self):
        return self.area_id


class Bin(models.Model):
    bin_id = models.CharField(max_length=20, unique=True, primary_key=True)
    bin_name = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)  # Liên kết với bảng Area
    pos_x = models.IntegerField(blank=True, null=True)  # Toạ độ X, có thể null
    pos_y = models.IntegerField(blank=True, null=True)  # Toạ độ Y, có thể null
    bin_w = models.IntegerField(blank=True, null=True)  # Bin Width
    bin_l = models.IntegerField(blank=True, null=True)  # Bin Length
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.CharField(max_length=100, null=True)  # Lưu tên hoặc ID người tạo
    update_at = models.DateTimeField(default=timezone.now)  # Tự động cập nhật thời gian mỗi khi bản ghi được cập nhật
    update_by = models.CharField(max_length=100, null=True)  # Lưu tên hoặc ID người cập nhật

    def __str__(self):
        return self.bin_name

class Attribute(models.Model):
    attr_id = models.CharField(max_length=20, unique=True, primary_key=True)
    attr_name = models.CharField(max_length=50)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.CharField(max_length=100, null=True)

class Area_Attribute(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    update_at = models.DateTimeField(default=timezone.now)
    update_by = models.CharField(max_length=100, null=True)

class Bin_Attr_Value(models.Model):
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    create_at = models.DateTimeField(default=timezone.now)
    create_by = models.CharField(max_length=100, null=True)


