document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("alumnosSearch");
  const btn = document.getElementById("btnLimpiarBusqueda");
  const mostrando = document.getElementById("mostrandoCount");
  const rows = document.querySelectorAll("#tablaAlumnos tbody tr");

  if (!input || !rows.length) return;

  function filtrar() {
    const term = (input.value || "").toLowerCase().trim();
    let visibles = 0;

    rows.forEach(tr => {
      const text = tr.textContent.toLowerCase();
      const show = text.includes(term);
      tr.style.display = show ? "" : "none";
      if (show) visibles++;
    });

    if (mostrando) mostrando.textContent = visibles;
  }

  input.addEventListener("input", filtrar);

  if (btn) {
    btn.addEventListener("click", () => {
      input.value = "";
      filtrar();
      input.focus();
    });
  }

  filtrar();
});