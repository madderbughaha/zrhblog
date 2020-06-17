from django.urls import path
from . import views

urlpatterns = [
    path('my_notifications/', views.my_notifications, name='my_notifications'),
    path('resolve_notify/', views.resolve_notify, name='resolve_notify'),
    path('mark_all_as_read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('delete_notify/', views.delete_notify, name='delete_notify')
]
