from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Producto, Pedido, DetallePedido


def es_admin(user):
    return user.is_staff or user.is_superuser

# ─── PÁGINA PRINCIPAL ────────────────────────────────────────────────────────
@login_required
def main(request):
    return render(request, 'store/main.html')

# ─── AUTH ────────────────────────────────────────────────────────────────────

def vista_login(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'store/login.html')


def vista_logout(request):
    logout(request)
    return redirect('login')


# ─── ENRUTADOR INICIO ────────────────────────────────────────────────────────

@login_required
def inicio(request):
    if es_admin(request.user):
        return redirect('admin_panel')
    return redirect('usuario_panel')


# ─── PANEL ADMINISTRADOR ─────────────────────────────────────────────────────

@login_required
@user_passes_test(es_admin, login_url='login')
def admin_panel(request):
    productos = Producto.objects.all()
    pedidos = Pedido.objects.select_related('usuario').all()
    usuarios = User.objects.all()

    contexto = {
        'productos': productos,
        'pedidos': pedidos,
        'usuarios': usuarios,
        'total_productos': productos.count(),
        'total_pedidos': pedidos.count(),
        'total_usuarios': usuarios.count(),
        'productos_activos': productos.filter(activo=True).count(),
    }
    return render(request, 'store/admin_panel.html', contexto)


@login_required
@user_passes_test(es_admin)
@require_POST
def crear_producto(request):
    data = json.loads(request.body)
    producto = Producto.objects.create(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        precio=data['precio'],
        stock=data.get('stock', 0),
    )
    return JsonResponse({'ok': True, 'id': producto.id, 'nombre': producto.nombre})


@login_required
@user_passes_test(es_admin)
@require_POST
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return JsonResponse({'ok': True})


@login_required
@user_passes_test(es_admin)
@require_POST
def cambiar_estado_pedido(request, pk):
    data = json.loads(request.body)
    pedido = get_object_or_404(Pedido, pk=pk)
    pedido.estado = data['estado']
    pedido.save()
    return JsonResponse({'ok': True, 'estado': pedido.estado})


# ─── PANEL USUARIO ───────────────────────────────────────────────────────────

@login_required
def usuario_panel(request):
    productos = Producto.objects.filter(activo=True)
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('detalles__producto')

    contexto = {
        'productos': productos,
        'pedidos': pedidos,
    }
    return render(request, 'store/usuario_panel.html', contexto)


@login_required
@require_POST
def crear_pedido(request):
    data = json.loads(request.body)
    items = data.get('items', [])

    if not items:
        return JsonResponse({'ok': False, 'error': 'Carrito vacío'})

    pedido = Pedido.objects.create(usuario=request.user)
    total = 0

    for item in items:
        producto = get_object_or_404(Producto, pk=item['id'], activo=True)
        cantidad = int(item['cantidad'])
        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
        )
        total += producto.precio * cantidad

    pedido.total = total
    pedido.save()

    return JsonResponse({'ok': True, 'pedido_id': pedido.id, 'total': str(total)})


# ─── VISTA VULNERABLE (solo para ejercicios educativos) ──────────────────────
from django.db import connection

def buscar_vulnerable(request):
    resultados = []
    query_ejecutada = ""
    error = ""

    if request.method == 'POST':
        termino = request.POST.get('termino', '')
        # ⚠️ VULNERABLE: concatenación directa de input del usuario
        query_ejecutada = f"SELECT id, nombre, precio, stock FROM store_producto WHERE nombre LIKE '%{termino}%'"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query_ejecutada)
                columnas = [col[0] for col in cursor.description]
                resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        except Exception as e:
            error = str(e)

    return render(request, 'store/buscar_vulnerable.html', {
        'resultados': resultados,
        'query_ejecutada': query_ejecutada,
        'error': error,
    })
