from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class GetReadNumOrReadObj:
    # 获取当前阅读量
    def get_read_num(self):
        ct = ContentType.objects.get_for_model(self)
        read_obj = ReadNum.objects.get_or_create(content_type=ct,
                                                 object_id=self.pk, defaults={'read_num': 0})[0]
        read_num = read_obj.read_num
        return read_num

    # 获取当天阅读量对象
    def get_date_read_num(self):
        date = timezone.now()
        ct = ContentType.objects.get_for_model(self)
        read_obj = ReadDetail.objects.get_or_create(content_type=ct,
                                                    object_id=self.pk, date=date, defaults={'read_num': 0})[0]
        read_num = read_obj.read_num
        return read_num


class ReadNum(models.Model):
    read_num = models.IntegerField(default=0, verbose_name='阅读量')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class ReadDetail(models.Model):
    date = models.DateField(default=timezone.now)
    read_num = models.IntegerField(default=0, verbose_name='阅读量')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
