from django.urls import path

from bands import views


urlpatterns = [
    path('', views.home, name='home_view'),
    path('user_dashboard/', views.UserDashboardView.as_view(),
         name=views.UserDashboardView.name),
    path('user_profile/', views.ProfileEditView.as_view(),
         name=views.ProfileEditView.name),
]
