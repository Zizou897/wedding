from django.urls import path
from . import views

app_name = 'brideGroom'

urlpatterns = [
    path('login/', views.login, name='index'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('Gio&Nadège/', views.transition, name='transition'),
    path('logout/', views.logout, name='logout'),
    path('export-excel/', views.export_rsvps_excel, name='export_rsvps_excel'),
    path('export-pdf/', views.export_rsvps_pdf, name='export_rsvps_pdf'),
    
    # ^Pour les arrivés
    path('dashboard/live/', views.dashboard_live, name='dashboard_live'),
    path('dashboard/live/data/', views.dashboard_live_data, name='dashboard_live_data'),
    
]