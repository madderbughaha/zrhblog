from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField(help_text='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True, help_text='评论时间')
    # 评论与用户关联
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    root = models.ForeignKey('self', related_name='root_comment', null=True, on_delete=models.CASCADE)
    # 自关联用来实现多级评论
    parent = models.ForeignKey('self', related_name='parent_comment', null=True, on_delete=models.CASCADE)
    # 回复对象与用户关联
    reply_to = models.ForeignKey(User, related_name='replies', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def get_model_name(self):
        return self.__class__.__name__

    def get_user(self):
        return self.user

    def get_url(self):
        return self.content_object.get_url()

    class Meta:
        ordering = ['comment_time']
