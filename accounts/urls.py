from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password-reset-validate/<uidb64>/<token>/', views.password_reset_validate, name='password_reset_validate'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]

