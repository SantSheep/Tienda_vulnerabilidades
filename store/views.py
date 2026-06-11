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


# ─── FUERZA BRUTA (vulnerable) ───────────────────────────────────────────────
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # ⚠️ vulnerable: sin protección CSRF para permitir scripts externos
def login_vulnerable(request):
    resultado = ""
    intentos_log = []

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user:
            resultado = f"✅ ÉXITO — usuario: {username} | contraseña: {password}"
        else:
            resultado = f"❌ Fallido — usuario: {username} | contraseña: {password}"

    return render(request, 'store/login_vulnerable.html', {
        'resultado': resultado,
    })


# ─── LOGIN SEGURO (con protección fuerza bruta) ───────────────────────────────
from django.core.cache import cache

def login_seguro(request):
    if request.user.is_authenticated:
        return redirect('main')

    error = ""
    bloqueado = False

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'login_intentos_{ip}_{username}'
        intentos = cache.get(cache_key, 0)

        if intentos >= 5:
            bloqueado = True
            error = f'Demasiados intentos. Espera 5 minutos.'
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                cache.delete(cache_key)
                login(request, user)
                return redirect('main')
            else:
                cache.set(cache_key, intentos + 1, timeout=300)  # bloqueo 5 min
                restantes = 5 - (intentos + 1)
                error = f'Credenciales incorrectas. Intentos restantes: {restantes}'

    return render(request, 'store/login_seguro.html', {
        'error': error,
        'bloqueado': bloqueado,
    })
    
    
    
    # ─── SESIONES VULNERABLE ─────────────────────────────────────────────────────
@login_required
def sesion_vulnerable(request):
    # ⚠️ Muestra el session ID completo y permite manipular datos de sesión
    session_id = request.COOKIES.get('sessionid', 'No encontrado')
    
    # ⚠️ Permite escribir datos arbitrarios en la sesión desde la URL
    clave = request.GET.get('set_key')
    valor = request.GET.get('set_val')
    if clave:
        request.session[clave] = valor

    datos_sesion = dict(request.session)

    return render(request, 'store/sesion_vulnerable.html', {
        'session_id': session_id,
        'datos_sesion': datos_sesion,
    })


# ─── SESIONES SEGURA ─────────────────────────────────────────────────────────
@login_required
def sesion_segura(request):
    # ✅ Solo muestra info necesaria, rota el session ID al cambiar datos
    session_id_parcial = request.COOKIES.get('sessionid', '')[:8] + '...'  # solo primeros 8 chars

    return render(request, 'store/sesion_segura.html', {
        'session_id_parcial': session_id_parcial,
        'usuario': request.user.username,
        'ultimo_acceso': request.session.get('ultimo_acceso', 'Primera visita'),
    })


# ─── SESSION FIXATION VULNERABLE ─────────────────────────────────────────────
def fixation_vulnerable(request):
    # ⚠️ Acepta session ID desde la URL y NO lo rota tras el login
    session_id_url = request.GET.get('sessionid')
    if session_id_url:
        request.session['forzado'] = True
        # simula fijar la sesión
        response = render(request, 'store/fixation_vulnerable.html', {
            'session_id': request.session.session_key,
            'forzado': session_id_url,
        })
        response.set_cookie('sessionid', session_id_url)  # ⚠️ fija la cookie
        return response

    return render(request, 'store/fixation_vulnerable.html', {
        'session_id': request.session.session_key,
        'forzado': None,
    })


# ─── SESSION FIXATION SEGURA ─────────────────────────────────────────────────
def fixation_segura(request):
    # ✅ Rota el session ID tras autenticar, ignora sessionid de la URL
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            # cycle_key() rota el session ID — previene session fixation
            request.session.cycle_key()
            login(request, user)
            return redirect('main')

    return render(request, 'store/fixation_segura.html')