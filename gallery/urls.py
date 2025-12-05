from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.waifus_gallery, name='waifus_gallery'),
    path('waifu/<str:name>/', views.waifu_detail, name='waifu_detail'),
    path('add_waifu/', views.add_waifu, name='add_waifu'),
    path('edit_waifu/<str:name>/', views.edit_waifu, name='edit_waifu'),
    path('set_featured/<str:name>/', views.set_featured, name='set_featured'),
    path('random/', views.random_waifu, name='random_waifu'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('info/', views.info, name='info'),
    path('backup/', views.backup, name='backup'),
]