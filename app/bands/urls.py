from django.urls import path

from bands import views


urlpatterns = [
    path('user_dashboard/', views.DashboardView.as_view(),
         name=views.DashboardView.name),
]
