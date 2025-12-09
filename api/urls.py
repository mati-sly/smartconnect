from django.urls import path
from . import views

# Configurar handler404
handler404 = views.handler404

urlpatterns = [
    # Información de la API
    path('info/', views.api_info, name='api-info'),
    
    # Sistema RFID
    path('validar-acceso/', views.validar_acceso_rfid, name='validar-acceso'),
    path('control-barrera/', views.control_barrera, name='control-barrera'),
    path('eventos-acceso/', views.eventos_acceso, name='eventos-acceso'),
    
    # CRUD Departamentos
    path('departamentos/', views.departamentos_list, name='departamentos-list'),
    path('departamentos/<int:pk>/', views.departamento_detail, name='departamento-detail'),
    
    # CRUD Usuarios
    path('usuarios/', views.usuarios_list, name='usuarios-list'),
    path('usuarios/<int:pk>/', views.usuario_detail, name='usuario-detail'),
    
    # CRUD Sensores
    path('sensores/', views.sensores_list, name='sensores-list'),
    path('sensores/<int:pk>/', views.sensor_detail, name='sensor-detail'),
]
