from django.urls import path

from users import views


urlpatterns = [
    path('signup/', views.SingUpView.as_view(), name=views.SingUpView.name),
    path('login/', views.LogInView.as_view(), name=views.LogInView.name),
    path('logout/', views.LogOutView.as_view(), name=views.LogOutView.name),
    path('password_change/', views.PasswordChangeView.as_view(),
         name=views.PasswordChangeView.name),
    path('dashboard/', views.DashboardView.as_view(),
         name=views.DashboardView.name),
]