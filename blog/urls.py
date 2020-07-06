from django.urls import path, re_path, include
from . import views

urlpatterns = [
    # http://localhost:8000
    path('', views.blog_list, name='blog_list'),
    path('<int:blog_pk>', views.blog_detail, name="blog_detail"),
    path('type/<int:blog_type_pk>', views.blog_with_type, name="blog_with_type"),
    path('date/<int:year>/<int:month>', views.blogs_with_date, name="blogs_with_date"),
    re_path(r'^search/', views.MySearchView(), name='my_search'),   # 类视图需要添加括号
]
