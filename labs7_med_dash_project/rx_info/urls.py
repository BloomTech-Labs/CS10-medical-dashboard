from django.urls import path
from . import views

urlpatterns = [
    path('pharmacy_info/', views.pharmacy_info, name='pharmacy_info'),
    path('PBM_info/', views.PBM_info, name='PBM_info'),
    path('pharmacy_results/', views.pharmacy_results, name='pharmacy_results'),
    path('PBM_results/', views.PBM_results, name='PBM_results'),
    path('background/', views.background, name='background'),
    ]
