from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from . import views_admin

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # Dashboard and profile URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # User administration URLs (admin only)
    path('admin/users/', views_admin.user_list, name='user_list'),
    path('admin/users/create/', views_admin.user_create, name='user_create'),
    path('admin/users/<int:pk>/', views_admin.user_detail, name='user_detail'),
    path('admin/users/<int:pk>/update/', views_admin.user_update, name='user_update'),
    path('admin/users/<int:pk>/delete/', views_admin.user_delete, name='user_delete'),
    path('admin/users/<int:pk>/roles/', views_admin.user_roles, name='user_roles'),
    path('admin/users/<int:pk>/leagues/', views_admin.user_leagues, name='user_leagues'),
    path('admin/users/<int:pk>/teams/', views_admin.user_teams, name='user_teams'),
]
