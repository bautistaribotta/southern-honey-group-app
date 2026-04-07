/**
 * -----------------------------------------------------------------------------
 * 1. UTILIDADES GENERALES (BÚSQUEDA, FILTRADO Y PAGINACIÓN)
 * -----------------------------------------------------------------------------
 */

// Selecciono los elementos del DOM necesarios
const inputBusqueda = document.getElementById('buscar-producto');
const filtroCategoria = document.getElementById('filtro-categoria');
const contenedorTabla = document.getElementById('tabla-productos-container');

/**
 * Creo esta función para buscar productos y aplicar los filtros de categoría
 * usando AJAX. No recarga la página entera.
 * @param {string|null} urlString - URL opcional (ej: para paginación).
 */
const buscar = (urlString = null) => {
  if (!inputBusqueda || !filtroCategoria || !contenedorTabla) return;

  const q = inputBusqueda.value;
  const categoria = filtroCategoria.value;
  let url;
  
  if (urlString) {
    url = new URL(urlString, window.location.origin);
  } else {
    url = new URL(window.location.href);
    url.searchParams.set('q', q);
    url.searchParams.set('categoria', categoria);
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
 * Creo esta función para que los enlaces de paginación funcionen por AJAX.
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

// Asigno los eventos iniciales a los inputs y selects
if (inputBusqueda) inputBusqueda.addEventListener('input', () => buscar());
if (filtroCategoria) filtroCategoria.addEventListener('change', () => buscar());
vincularPaginacion();

/**
 * -----------------------------------------------------------------------------
 * 2. CONTROLADORES DE PANELES (NUEVO/EDITAR)
 * -----------------------------------------------------------------------------
 */

/**
 * Creo esta función para limpiar el panel lateral y prepararlo para registrar
 * un nuevo producto desde cero.
 */
const prepararPanelNuevoProducto = () => {
  // Restauro los textos originales
  document.querySelector('#slide-over-panel h3').innerText = 'Nuevo Producto';
  document.querySelector('#slide-over-panel .texto-cabecera p').innerText = 'Complete los detalles para el inventario';
  document.querySelector('.boton-primario').innerText = 'Guardar Producto';
  document.querySelector('.icono-contenedor span').innerText = 'inventory_2';

  // Limpio el formulario y el ID oculto
  document.getElementById('form-producto').reset();
  document.getElementById('id_producto').value = '';
  
  if (typeof abrirSlideOver === 'function') abrirSlideOver();
};

/**
 * Creo esta función para traer la información de un producto desde la API
 * y llenar los campos del panel lateral para editarlo.
 * @param {string|number} id - El ID del producto
 */
const prepararPanelEditarProducto = (id) => {
  fetch(`/api/productos/${id}/`)
    .then((response) => response.json())
    .then((producto) => {
      // Actualizo textos e iconos para indicar "Edición"
      document.querySelector('#slide-over-panel h3').innerText = 'Editar Producto';
      document.querySelector('#slide-over-panel .texto-cabecera p').innerText = 'Modifique los datos del producto';
      document.querySelector('.boton-primario').innerText = 'Actualizar Producto';
      document.querySelector('.icono-contenedor span').innerText = 'edit_square';
      document.querySelector('label[for="stock"]').innerText = 'Stock disponible';

      // Relleno el formulario con los datos reales
      document.getElementById('id_producto').value = producto.id;
      document.getElementById('nombre').value = producto.nombre;
      document.getElementById('categoria').value = producto.categoria;
      document.getElementById('precio').value = producto.precio;
      document.getElementById('stock').value = producto.cantidad;

      if (typeof abrirSlideOver === 'function') abrirSlideOver();
    })
    .catch((error) => {
      console.error(error);
      if (typeof crearToast === 'function') {
        crearToast('Error al cargar los datos del producto', 'error');
      }
    });
};

/**
 * -----------------------------------------------------------------------------
 * 3. DELEGACIÓN DE EVENTOS (TABLA)
 * -----------------------------------------------------------------------------
 */

/**
 * Agrego un event listener general para escuchar los clicks de los botones
 * en cualquier parte de la tabla sin tener que asignar un evento por fila.
 */
document.addEventListener('click', (e) => {
  const botonEditar = e.target.closest('.boton-icono.editar');
  const botonEliminar = e.target.closest('.boton-icono.eliminar');

  if (botonEditar) {
    const id = botonEditar.dataset.id;
    prepararPanelEditarProducto(id);
  }

  if (botonEliminar) {
    const id = botonEliminar.dataset.id;
    const nombre = botonEliminar.dataset.nombre;

    // Configuro el panel modal de eliminación
    document.getElementById('id_eliminar').value = id;
    document.getElementById('texto-confirmacion-eliminar').innerHTML = `¿Confirma que quiere eliminar el producto <b>${nombre}</b>?`;

    if (typeof abrirPanelEliminar === 'function') abrirPanelEliminar();
  }
});

// Hago accesibles las funciones que el HTML llama mediante "onclick"
window.prepararPanelNuevoProducto = prepararPanelNuevoProducto;