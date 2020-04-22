from django.urls import path

from bands import views


urlpatterns = [
    path('', views.HomeView.as_view(), name=views.HomeView.name),
    path('user_dashboard/', views.UserDashboardView.as_view(),
         name=views.UserDashboardView.name),
    path('user_profile/', views.ProfileEditView.as_view(),
         name=views.ProfileEditView.name),
    path('musicians/', views.MusiciansView.as_view(), name=views.MusiciansView.name),
    path('musicians/<int:id>/', views.MusiciansView.as_view(), name=views.MusiciansView.name),
    path('bands_dashboard/', views.BandsDashboardView.as_view(),
         name=views.BandsDashboardView.name),
    path('band_edit/', views.BandEditView.as_view(), name=views.BandEditView.name),
    path('band_edit/<int:id>/', views.BandEditView.as_view(), name=views.BandEditView.name),
]
