// Autocompletado de clientes con busqueda server-side (endpoint api/clientes/buscar/).
// Reemplaza al <select> que listaba todos los clientes: con miles de registros, ese
// select inflaba el HTML y no tenia busqueda. Aca el input visible busca por AJAX y el
// id del cliente elegido viaja en un input hidden (data-target). Reutiliza los estilos
// del desplegable de ciudades (.lista-autocompletado-ciudades).

(function () {
  const URL_API = '/api/clientes/buscar/';
  const MINIMO_CARACTERES = 1;
  const RETARDO_MS = 300;

  async function buscarClientes(texto, senal) {
    const parametros = new URLSearchParams({ q: texto });
    const respuesta = await fetch(`${URL_API}?${parametros}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      signal: senal,
    });
    if (!respuesta.ok) return [];

    const datos = await respuesta.json();
    return datos.clientes || [];
  }

  function inicializarAutocompletadoCliente(input) {
    const contenedor = input.parentElement;
    contenedor.classList.add('contenedor-autocompletado-ciudades');

    // Input hidden que lleva el id del cliente al backend
    const hidden = document.querySelector(input.dataset.target);

    const lista = document.createElement('ul');
    lista.className = 'lista-autocompletado-ciudades';
    lista.hidden = true;
    input.insertAdjacentElement('afterend', lista);

    let sugerencias = [];
    let indiceResaltado = -1;
    let temporizador = null;
    let controlador = null;

    function ocultarLista() {
      lista.hidden = true;
      indiceResaltado = -1;
    }

    function seleccionar(cliente) {
      input.value = cliente.texto;
      if (hidden) hidden.value = cliente.id;
      ocultarLista();
    }

    function resaltar(indice) {
      const opciones = lista.querySelectorAll('li');
      opciones.forEach((opcion) => opcion.classList.remove('resaltada'));
      if (indice >= 0 && indice < opciones.length) {
        opciones[indice].classList.add('resaltada');
        opciones[indice].scrollIntoView({ block: 'nearest' });
      }
      indiceResaltado = indice;
    }

    function mostrarSugerencias(clientes) {
      sugerencias = clientes;

      if (clientes.length === 0) {
        ocultarLista();
        return;
      }

      lista.replaceChildren(
        ...clientes.map((cliente) => {
          const opcion = document.createElement('li');
          opcion.textContent = cliente.texto;
          // mousedown en lugar de click para ganarle al blur del input
          opcion.addEventListener('mousedown', (evento) => {
            evento.preventDefault();
            seleccionar(cliente);
          });
          return opcion;
        })
      );

      // Posiciono la lista justo debajo del input dentro de su contenedor
      lista.style.top = `${input.offsetTop + input.offsetHeight + 4}px`;
      lista.style.left = `${input.offsetLeft}px`;
      lista.style.width = `${input.offsetWidth}px`;
      lista.hidden = false;
      indiceResaltado = -1;
    }

    input.addEventListener('input', () => {
      clearTimeout(temporizador);

      // Al tipear se invalida la seleccion previa: el id solo es valido si se elige
      // una opcion del desplegable. Vacio queda como "Sin cliente".
      if (hidden) hidden.value = '';

      const texto = input.value.trim();
      if (texto.length < MINIMO_CARACTERES) {
        ocultarLista();
        return;
      }

      temporizador = setTimeout(async () => {
        if (controlador) controlador.abort();
        controlador = new AbortController();

        try {
          const clientes = await buscarClientes(texto, controlador.signal);
          mostrarSugerencias(clientes);
        } catch (error) {
          // Peticion abortada o sin conexion: no se muestran sugerencias
          ocultarLista();
        }
      }, RETARDO_MS);
    });

    input.addEventListener('keydown', (evento) => {
      if (lista.hidden) return;

      const totalOpciones = sugerencias.length;

      if (evento.key === 'ArrowDown') {
        evento.preventDefault();
        resaltar((indiceResaltado + 1) % totalOpciones);
      } else if (evento.key === 'ArrowUp') {
        evento.preventDefault();
        resaltar((indiceResaltado - 1 + totalOpciones) % totalOpciones);
      } else if (evento.key === 'Enter') {
        if (indiceResaltado >= 0) {
          evento.preventDefault();
          seleccionar(sugerencias[indiceResaltado]);
        }
      } else if (evento.key === 'Escape') {
        ocultarLista();
      }
    });

    input.addEventListener('blur', ocultarLista);
  }

  // Disponible globalmente para inputs creados dinamicamente
  window.inicializarAutocompletadoCliente = inicializarAutocompletadoCliente;

  document.addEventListener('DOMContentLoaded', () => {
    document
      .querySelectorAll('input[data-autocompletar-cliente]')
      .forEach(inicializarAutocompletadoCliente);
  });
})();
