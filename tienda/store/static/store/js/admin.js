// ── CSRF helper ────────────────────────────────────────────────
function getCsrf() {
  return document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? '';
}

async function apiFetch(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrf(),
    },
    body: JSON.stringify(body),
  });
  return res.json();
}

// ── MODAL PRODUCTO ──────────────────────────────────────────────
function abrirModalProducto() {
  document.getElementById('modal-producto').style.display = 'flex';
  document.getElementById('modal-msg').style.display = 'none';
}

function cerrarModalProducto() {
  document.getElementById('modal-producto').style.display = 'none';
  ['prod-nombre', 'prod-desc', 'prod-precio', 'prod-stock'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

async function guardarProducto() {
  const nombre  = document.getElementById('prod-nombre').value.trim();
  const desc    = document.getElementById('prod-desc').value.trim();
  const precio  = parseFloat(document.getElementById('prod-precio').value);
  const stock   = parseInt(document.getElementById('prod-stock').value) || 0;

  const msg = document.getElementById('modal-msg');

  if (!nombre || isNaN(precio) || precio < 0) {
    msg.textContent = 'Nombre y precio son obligatorios.';
    msg.className = 'alert alert-error';
    msg.style.display = 'block';
    return;
  }

  const data = await apiFetch('/admin-panel/producto/crear/', { nombre, descripcion: desc, precio, stock });

  if (data.ok) {
    // Agregar fila a la tabla sin recargar
    const tbody = document.querySelector('#tabla-productos tbody');
    const emptyRow = tbody.querySelector('.empty-msg');
    if (emptyRow) emptyRow.parentElement.remove();

    const tr = document.createElement('tr');
    tr.id = `row-prod-${data.id}`;
    tr.innerHTML = `
      <td>${data.id}</td>
      <td>${escHtml(nombre)}</td>
      <td>$${precio.toFixed(2)}</td>
      <td>${stock}</td>
      <td><span class="badge badge-ok">Activo</span></td>
      <td><button class="btn btn-danger btn-xs" onclick="eliminarProducto(${data.id})">Eliminar</button></td>
    `;
    tbody.appendChild(tr);
    cerrarModalProducto();
  } else {
    msg.textContent = 'Error al guardar.';
    msg.className = 'alert alert-error';
    msg.style.display = 'block';
  }
}

// ── ELIMINAR PRODUCTO ───────────────────────────────────────────
async function eliminarProducto(id) {
  if (!confirm('¿Eliminar este producto?')) return;
  const data = await apiFetch(`/admin-panel/producto/${id}/eliminar/`, {});
  if (data.ok) {
    document.getElementById(`row-prod-${id}`)?.remove();
  }
}

// ── CAMBIAR ESTADO PEDIDO ───────────────────────────────────────
async function cambiarEstado(id, estado) {
  const data = await apiFetch(`/admin-panel/pedido/${id}/estado/`, { estado });
  if (data.ok) {
    const badge = document.getElementById(`badge-ped-${id}`);
    if (badge) badge.textContent = data.estado;
  }
}

// ── UTIL ────────────────────────────────────────────────────────
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Cerrar modal al hacer click fuera
document.getElementById('modal-producto').addEventListener('click', function(e) {
  if (e.target === this) cerrarModalProducto();
});
