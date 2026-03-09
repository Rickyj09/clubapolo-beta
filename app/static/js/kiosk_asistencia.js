// app/static/js/kiosk_asistencia.js
(() => {
  const $q = document.getElementById('q');
  const $fecha = document.getElementById('fecha');
  const $sucursal = document.getElementById('sucursal');
  const $results = document.getElementById('results');

  const $btnMarcar = document.getElementById('btnMarcar');
  const $btnLimpiar = document.getElementById('btnLimpiar');
  const $seleccion = document.getElementById('seleccion');
  const $obs = document.getElementById('obs');

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

  let seleccionado = null;
  let estadoActual = 'P';
  let debounceTimer = null;

  function showToast(msg) {
    const body = document.getElementById('toastBody');
    const toastEl = document.getElementById('toastOk');
    if (!body || !toastEl || !window.bootstrap) {
      alert(msg); // fallback si bootstrap JS no está
      return;
    }
    body.innerText = msg;
    const t = new bootstrap.Toast(toastEl, { delay: 2200 });
    t.show();
  }

  function setEstado(estado) {
    estadoActual = estado;
    document.querySelectorAll('[data-estado]').forEach(btn => {
      btn.classList.remove('active');
      if (btn.getAttribute('data-estado') === estado) btn.classList.add('active');
    });
  }

  function limpiar() {
    $q.value = '';
    $results.innerHTML = '<div class="text-muted p-3">Escribe para buscar…</div>';
    seleccionado = null;
    $seleccion.innerText = '—';
    $btnMarcar.disabled = true;
    $obs.value = '';
    setEstado('P');
    $q.focus();
  }

  function renderResults(items) {
    if (!items || items.length === 0) {
      $results.innerHTML = '<div class="text-muted p-3">Sin resultados.</div>';
      return;
    }

    $results.innerHTML = '';
    items.forEach(a => {
      const identidad = a.identidad ? `<span class="mono">${a.identidad}</span>` : '<span class="text-muted">s/identidad</span>';
      const el = document.createElement('button');
      el.type = 'button';
      el.className = 'list-group-item list-group-item-action';
      el.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="fw-semibold">${a.nombre}</div>
            <div class="text-muted small">ID: ${a.id} · ${identidad}</div>
          </div>
          <div><span class="badge text-bg-primary">Seleccionar</span></div>
        </div>
      `;

      el.addEventListener('click', () => {
        seleccionado = a;
        $seleccion.innerText = `${a.nombre} (${a.identidad || 's/identidad'})`;
        $btnMarcar.disabled = false;
      });

      $results.appendChild(el);
    });
  }

  async function buscar() {
    const q = $q.value.trim();
    if (q.length < 2) {
      $results.innerHTML = '<div class="text-muted p-3">Escribe al menos 2 caracteres.</div>';
      return;
    }

    $results.innerHTML = '<div class="text-muted p-3">Buscando…</div>';
    seleccionado = null;
    $seleccion.innerText = '—';
    $btnMarcar.disabled = true;

    const url = `/kiosk/buscar?q=${encodeURIComponent(q)}&sucursal_id=${encodeURIComponent($sucursal.value)}`;
    const res = await fetch(url);
    const data = await res.json();

    if (data.aviso) {
      const toastEl = document.getElementById("toastAviso");
      document.getElementById("toastTitle").innerText = data.aviso.title || "Aviso";
      document.getElementById("toastBody").innerText = data.aviso.text || "";

  // pintar estilo según tipo
  toastEl.classList.remove("text-bg-warning", "text-bg-danger");
  if (data.aviso.type === "danger") toastEl.classList.add("text-bg-danger");
  else toastEl.classList.add("text-bg-warning");

  const toast = new bootstrap.Toast(toastEl, { delay: 6000 });
  toast.show();
}

    if (!data.ok) {
      $results.innerHTML = `<div class="text-danger p-3">Error: ${data.error || 'No se pudo buscar'}</div>`;
      return;
    }

    renderResults(data.data);
  }

  async function marcar() {
    if (!seleccionado) return;

    const payload = {
      alumno_id: seleccionado.id,
      fecha: $fecha.value,
      sucursal_id: parseInt($sucursal.value, 10),
      estado: estadoActual,
      observacion: $obs.value.trim()
    };

    $btnMarcar.disabled = true;

    const res = await fetch('/kiosk/marcar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-CSRF-Token': csrfToken
      },
      body: JSON.stringify(payload)
    });

    const contentType = res.headers.get("content-type") || "";
const text = await res.text();

if (!res.ok) {
  // muestra el motivo real: 302/401/403/500
  alert(`Error HTTP ${res.status}:\n${text.substring(0, 300)}`);
  $btnMarcar.disabled = false;
  return;
}

if (!contentType.includes("application/json")) {
  alert(`Respuesta no JSON (probable redirect/login/CSRF).\n\n${text.substring(0, 300)}`);
  $btnMarcar.disabled = false;
  return;
}

const data = JSON.parse(text);

    if (!data.ok) {
      showToast(`❌ Error: ${data.error || 'No se pudo guardar'}`);
      $btnMarcar.disabled = false;
      return;
    }

    showToast(`✅ ${seleccionado.nombre} · Estado ${payload.estado} · ${payload.fecha}`);
    limpiar();
  }

  // Eventos
  $btnMarcar.addEventListener('click', marcar);
  $btnLimpiar.addEventListener('click', limpiar);

  document.querySelectorAll('[data-estado]').forEach(btn => {
    btn.addEventListener('click', () => setEstado(btn.getAttribute('data-estado')));
  });

  $q.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      buscar();
    }
  });

  $q.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const q = $q.value.trim();
      if (q.length >= 2) buscar();
    }, 250);
  });

  $sucursal.addEventListener('change', () => limpiar());

  window.addEventListener('load', () => {
    setEstado('P');
    $q.focus();
  });
})();