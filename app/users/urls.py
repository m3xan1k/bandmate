from django.urls import path
from django.contrib.auth import views as auth_views

from users import views


urlpatterns = [
    path('signup/', views.SingUpView.as_view(), name=views.SingUpView.name),
    path('login/', views.LogInView.as_view(), name=views.LogInView.name),
    path('logout/', views.LogOutView.as_view(), name=views.LogOutView.name),
    path('password_change/', views.PasswordChangeView.as_view(),
         name=views.PasswordChangeView.name),
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('dashboard/', views.DashboardView.as_view(),
         name=views.DashboardView.name),
]
