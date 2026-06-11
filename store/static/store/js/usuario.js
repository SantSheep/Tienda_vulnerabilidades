// ── ESTADO DEL CARRITO ──────────────────────────────────────────
let carrito = {}; // { id: { nombre, precio, cantidad } }

function getCsrf() {
  return document.getElementById('csrf-token')?.value ?? '';
}

// ── CARRITO UI ──────────────────────────────────────────────────
function abrirCarrito() {
  document.getElementById('carrito-overlay').style.display = 'block';
  document.getElementById('carrito-panel').classList.add('open');
  document.getElementById('carrito-msg').style.display = 'none';
}

function cerrarCarrito() {
  document.getElementById('carrito-overlay').style.display = 'none';
  document.getElementById('carrito-panel').classList.remove('open');
}

function agregarAlCarrito(id, nombre, precio) {
  if (carrito[id]) {
    carrito[id].cantidad += 1;
  } else {
    carrito[id] = { nombre, precio: parseFloat(precio), cantidad: 1 };
  }
  renderCarrito();
  abrirCarrito();
}

function quitarDelCarrito(id) {
  delete carrito[id];
  renderCarrito();
}

function renderCarrito() {
  const container = document.getElementById('carrito-items');
  const totalEl   = document.getElementById('carrito-total');
  const countEl   = document.getElementById('carrito-count');

  const ids = Object.keys(carrito);

  if (ids.length === 0) {
    container.innerHTML = '<p class="empty-msg">El carrito está vacío</p>';
    totalEl.textContent = '0.00';
    countEl.textContent = '0';
    return;
  }

  let total = 0;
  let html  = '';

  ids.forEach(id => {
    const item = carrito[id];
    const sub  = item.precio * item.cantidad;
    total += sub;
    html += `
      <div class="carrito-item">
        <div class="carrito-item-info">
          <span>${escHtml(item.nombre)}</span>
          <span>${item.cantidad} × <span class="item-precio">$${item.precio.toFixed(2)}</span></span>
        </div>
        <button class="btn btn-ghost btn-xs" onclick="quitarDelCarrito(${id})">✕</button>
      </div>`;
  });

  container.innerHTML = html;
  totalEl.textContent = total.toFixed(2);
  countEl.textContent = ids.length;
}

// ── REALIZAR PEDIDO ─────────────────────────────────────────────
async function realizarPedido() {
  const msg = document.getElementById('carrito-msg');

  if (Object.keys(carrito).length === 0) {
    mostrarMsg(msg, 'El carrito está vacío.', 'error');
    return;
  }

  const items = Object.entries(carrito).map(([id, item]) => ({
    id: parseInt(id),
    cantidad: item.cantidad,
  }));

  try {
    const res = await fetch('/tienda/pedido/crear/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrf(),
      },
      body: JSON.stringify({ items }),
    });
    const data = await res.json();

    if (data.ok) {
      mostrarMsg(msg, `✅ Pedido #${data.pedido_id} creado por $${data.total}`, 'ok');
      carrito = {};
      renderCarrito();
      setTimeout(() => { location.reload(); }, 1800);
    } else {
      mostrarMsg(msg, data.error || 'Error al crear el pedido.', 'error');
    }
  } catch {
    mostrarMsg(msg, 'Error de conexión.', 'error');
  }
}

// ── UTIL ────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function mostrarMsg(el, texto, tipo) {
  el.textContent = texto;
  el.className = `alert alert-${tipo}`;
  el.style.display = 'block';
}
