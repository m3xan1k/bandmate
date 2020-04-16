from django.urls import path

from users import views


urlpatterns = [
    path('signup/', views.SingUpView.as_view(), name=views.SingUpView.name),
    path('signin/', views.SignInView.as_view(), name=views.SignInView.name),
    path('dashboard/', views.DashboardView.as_view(), name=views.DashboardView.name),
]
