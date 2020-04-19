from django.urls import path

from bands import views


urlpatterns = [
    path('user_dashboard/', views.UserDashboardView.as_view(),
         name=views.UserDashboardView.name),
]
