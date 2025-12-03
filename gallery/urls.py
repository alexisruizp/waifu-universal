from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.waifus_gallery, name='waifus_gallery'),
    path('waifu/<str:name>/', views.waifu_detail, name='waifu_detail'),
    path('add_waifu/', views.add_waifu, name='add_waifu'),
    path('edit_waifu/<str:name>/', views.edit_waifu, name='edit_waifu'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('info/', views.info, name='info'),
    path('login/', auth_views.LoginView.as_view(template_name='gallery/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='waifus_gallery'), name='logout'),
    path('register/', views.register, name='register'),
    path('backup/', views.backup, name='backup'),
]