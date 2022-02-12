from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'), #ip/accounts ก็จะไปที่ dashboard หรือ ip/accounts/dashboard ก้ได้เหมือนกัน 
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword_valid/<uidb64>/<token>/', views.resetpassword_valid, name='resetpassword_valid'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
] 
