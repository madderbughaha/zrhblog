from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mdeditor.fields import MDTextField
from read_count.models import GetReadNumOrReadObj, ReadDetail
from django.contrib.contenttypes.fields import GenericRelation


class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name


class Blog(models.Model, GetReadNumOrReadObj):
    title = models.CharField(max_length=50, verbose_name='文章标题')
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE, verbose_name='文章类型')
    content = MDTextField(verbose_name='文章内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    create_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    read_details = GenericRelation(ReadDetail)

    def __str__(self):
        return "<Blog: %s>" % self.title

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    def get_user(self):
        return self.author

    class Meta:
        ordering = ['-create_time']

