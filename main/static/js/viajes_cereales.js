/**
 * -----------------------------------------------------------------------------
 * BÚSQUEDA, FILTRADO POR CEREAL Y PAGINACIÓN (AJAX)
 * Mismo comportamiento que la tabla de viajes: busca, filtra y pagina sin
 * recargar la página entera, y mantiene el bloqueo de los botones del footer.
 * -----------------------------------------------------------------------------
 */

const inputBusqueda = document.getElementById('buscar-viaje-cereal');
const filtroCereal = document.getElementById('filtro-cereal');
const contenedorTabla = document.getElementById('tabla-viajes-cereales-container');

/**
 * Busca viajes de cereales aplicando texto y filtro de cereal mediante AJAX.
 * @param {string|null} urlString - URL opcional (ej: para paginación).
 */
const buscar = (urlString = null) => {
  if (!inputBusqueda || !filtroCereal || !contenedorTabla) return;

  const q = inputBusqueda.value;
  const cereal = filtroCereal.value;
  let url;

  if (urlString) {
    url = new URL(urlString, window.location.origin);
  } else {
    url = new URL(window.location.href);
    url.searchParams.set('q', q);
    if (cereal) {
      url.searchParams.set('cereal', cereal);
    } else {
      url.searchParams.delete('cereal');
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

// Chips de tipo de cereal
const chipsCereal = document.getElementById('chips-cereal');
if (chipsCereal) {
  chipsCereal.addEventListener('click', (e) => {
    const chip = e.target.closest('.prod-chip');
    if (!chip) return;

    chipsCereal.querySelectorAll('.prod-chip').forEach((c) => c.classList.remove('is-active'));
    chip.classList.add('is-active');

    if (filtroCereal) filtroCereal.value = chip.dataset.cereal;
    buscar();
  });
}

vincularPaginacion();
