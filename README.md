# TiendaTest 🛒

Tienda virtual básica para testear bases de datos con Django.

## Estructura

```
tienda/
├── tienda/          ← configuración del proyecto
│   ├── settings.py
│   └── urls.py
├── store/           ← la aplicación principal
│   ├── models.py    ← Producto, Pedido, DetallePedido
│   ├── views.py     ← login, admin_panel, usuario_panel
│   ├── urls.py
│   ├── templates/store/
│   │   ├── login.html
│   │   ├── admin_panel.html
│   │   └── usuario_panel.html
│   └── static/store/
│       ├── css/main.css
│       └── js/admin.js  &  usuario.js
├── manage.py
└── requirements.txt
```

## Pasos para correr

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear tablas en la base de datos (SQLite por defecto)
python manage.py migrate

# 3. Crear un superusuario (admin)
python manage.py createsuperuser

# 4. (Opcional) Crear un usuario normal desde la shell
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('cliente', password='1234')

# 5. Arrancar el servidor
python manage.py runserver
```

Abrir en el navegador: http://127.0.0.1:8000/login/

## Roles

| Rol     | Cómo crearlo                          | Panel que ve        |
|---------|---------------------------------------|---------------------|
| Admin   | `createsuperuser` o marcar `is_staff` | `/admin-panel/`     |
| Usuario | `create_user` normal                  | `/tienda/`          |

## Cambiar a PostgreSQL

En `tienda/settings.py`, reemplaza el bloque DATABASES:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tienda_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Instala el driver: `pip install psycopg2-binary`

## Modelos en la BD

- **Producto**: nombre, descripción, precio, stock, activo
- **Pedido**: usuario (FK), estado, total, fecha
- **DetallePedido**: pedido (FK), producto (FK), cantidad, precio_unitario
