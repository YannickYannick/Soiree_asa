"""URLs for events app."""

from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Event management
    path('event/<int:pk>/', views.event_detail, name='event_detail'),
    path('event/create/', views.event_create, name='event_create'),
    
    # Modules
    path('event/<int:pk>/simulation/', views.simulation, name='simulation'),
    path('event/<int:pk>/pricing/', views.pricing, name='pricing'),
    path('event/<int:pk>/tables/', views.tables, name='tables'),
    path('event/<int:pk>/instagram/', views.instagram, name='instagram'),
    path('event/<int:pk>/budget/', views.budget, name='budget'),
    path('event/<int:pk>/sales/', views.sales, name='sales'),
    path('event/<int:pk>/outils/', views.outils, name='outils'),
    
    # API endpoints for AJAX updates
    path('api/event/<int:pk>/simulate/', views.api_simulate, name='api_simulate'),
    path('api/event/<int:pk>/update-table/', views.api_update_table, name='api_update_table'),
    path('api/event/<int:pk>/update-budget/', views.api_update_budget, name='api_update_budget'),
    path('api/event/<int:pk>/update-instagram/', views.api_update_instagram, name='api_update_instagram'),
    path('api/event/<int:pk>/sales-data/', views.api_sales_data, name='api_sales_data'),
]
