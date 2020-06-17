from django.urls import path
from . import views


urlpatterns = [
    # http://localhost:8000
    path('like_change', views.like_change, name='like_change'),
]