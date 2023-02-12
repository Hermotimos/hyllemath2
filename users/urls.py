from django.urls import path
from users import views


app_name = 'users'
urlpatterns = [
    path('', views.home_view, name='home'),
    # path('dupa/', views.dupa_view, name='dupa'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('change_password/', views.change_password_view, name='change-password'),
    # path('edit-profile/', views.edit_profile_view, name='edit-profile'),
    path('edit-user/', views.edit_user_view, name='edit-user'),
    # path('switch-profile:<int:profile_id>/', views.switch_profile, name='switch-profile'),
]
