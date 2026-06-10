/**
 * -----------------------------------------------------------------------------
 * BÚSQUEDA, FILTRADO POR ESTADO Y PAGINACIÓN (AJAX)
 * -----------------------------------------------------------------------------
 */

const inputBusqueda = document.getElementById('buscar-viaje');
const filtroEstado = document.getElementById('filtro-estado');
const contenedorTabla = document.getElementById('tabla-viajes-container');

/**
 * Busca viajes aplicando texto y filtro de estado mediante AJAX, sin recargar
 * la página entera.
 * @param {string|null} urlString - URL opcional (ej: para paginación).
 */
const buscar = (urlString = null) => {
  if (!inputBusqueda || !filtroEstado || !contenedorTabla) return;

  const q = inputBusqueda.value;
  const estado = filtroEstado.value;
  let url;

  if (urlString) {
    url = new URL(urlString, window.location.origin);
  } else {
    url = new URL(window.location.href);
    url.searchParams.set('q', q);
    if (estado) {
      url.searchParams.set('estado', estado);
    } else {
      url.searchParams.delete('estado');
    }
    url.searchParams.delete('page');
  }

  fetch(url, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then((response) => response.text())
    .then((html) => {
      contenedorTabla.innerHTML = html;
      window.history.pushState({}, '', url);
      vincularPaginacion();
    })
    .catch((error) => console.error('Error en la búsqueda:', error));
};

/**
 * Hace que los enlaces de paginación funcionen por AJAX.
 */
const vincularPaginacion = () => {
  if (!contenedorTabla) return;
  const linksPaginacion = contenedorTabla.querySelectorAll('.paginacion-botones a');

  linksPaginacion.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      buscar(link.href);
    });
  });
};

if (inputBusqueda) inputBusqueda.addEventListener('input', () => buscar());

// Chips de estado
const chipsEstado = document.getElementById('chips-estado');
if (chipsEstado) {
  chipsEstado.addEventListener('click', (e) => {
    const chip = e.target.closest('.prod-chip');
    if (!chip) return;

    chipsEstado.querySelectorAll('.prod-chip').forEach((c) => c.classList.remove('is-active'));
    chip.classList.add('is-active');

    if (filtroEstado) filtroEstado.value = chip.dataset.estado;
    buscar();
  });
}

vincularPaginacion();
