from django.urls import path

from board import views


urlpatterns = [
    path('announcement_dashboard/', views.AnnouncementDashboardView.as_view(),
         name=views.AnnouncementDashboardView.name),
    path('announcement_edit/', views.AnnouncementEditView.as_view(),
         name=views.AnnouncementEditView.name),
]
