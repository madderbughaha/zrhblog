import datetime
from .models import Blog
from haystack import indexes


class BlogIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # 返回所查询的模型
    def get_model(self):  # 重载get_model方法(必要)
        return Blog

    # 需要查询哪些数据
    def index_queryset(self, using=None):   # (必要)
        return self.get_model().objects.all()