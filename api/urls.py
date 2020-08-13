from django.urls import include, path
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register('users', views.UsersViewSet)
router.register('blog', views.BlogListViewSet)
router.register('blog_type', views.BlogTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('home/', views.HomeDataView.as_view(), name='home_data'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
