from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('', views.inicio, name='inicio'),
    path('login/', views.vista_login, name='login'),
    path('logout/', views.vista_logout, name='logout'),

    # Admin
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/producto/crear/', views.crear_producto, name='crear_producto'),
    path('admin-panel/producto/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('admin-panel/pedido/<int:pk>/estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

    # Usuario
    path('tienda/', views.usuario_panel, name='usuario_panel'),
    path('tienda/pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('buscar/', views.buscar_vulnerable, name='buscar_vulnerable'),
]
