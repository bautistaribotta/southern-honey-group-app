// Autocompletado de ciudades argentinas usando la API Georef (datos.gob.ar).
// Muestra un desplegable propio con sugerencias debajo del input mientras
// el usuario escribe. No usa datalist porque los formularios del sitio tienen
// autocomplete="off" y el navegador suprime sus sugerencias.

(function () {
  const URL_API = 'https://apis.datos.gob.ar/georef/api/localidades';
  const MINIMO_CARACTERES = 3;
  const RETARDO_MS = 300;

  async function buscarCiudades(texto, senal) {
    const parametros = new URLSearchParams({
      nombre: texto,
      campos: 'nombre',
      max: '10',
      orden: 'nombre'
    });

    const respuesta = await fetch(`${URL_API}?${parametros}`, { signal: senal });
    if (!respuesta.ok) return [];

    const datos = await respuesta.json();
    return datos.localidades.map((localidad) => localidad.nombre);
  }

  function inicializarAutocompletadoCiudad(input) {
    const contenedor = input.parentElement;
    contenedor.classList.add('contenedor-autocompletado-ciudades');

    const lista = document.createElement('ul');
    lista.className = 'lista-autocompletado-ciudades';
    lista.hidden = true;
    input.insertAdjacentElement('afterend', lista);

    let indiceResaltado = -1;
    let temporizador = null;
    let controlador = null;

    function ocultarLista() {
      lista.hidden = true;
      indiceResaltado = -1;
    }

    function seleccionar(nombre) {
      input.value = nombre;
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

    function mostrarSugerencias(nombres) {
      if (nombres.length === 0) {
        ocultarLista();
        return;
      }

      lista.replaceChildren(
        ...nombres.map((nombre) => {
          const opcion = document.createElement('li');
          opcion.textContent = nombre;
          // mousedown en lugar de click para ganarle al blur del input
          opcion.addEventListener('mousedown', (evento) => {
            evento.preventDefault();
            seleccionar(nombre);
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

      const texto = input.value.trim();
      if (texto.length < MINIMO_CARACTERES) {
        ocultarLista();
        return;
      }

      temporizador = setTimeout(async () => {
        if (controlador) controlador.abort();
        controlador = new AbortController();

        try {
          const nombres = await buscarCiudades(texto, controlador.signal);

          // Evito sugerir nombres que superen el maximo permitido por el input
          const maximo = input.maxLength > 0 ? input.maxLength : Infinity;
          const unicos = [...new Set(nombres)].filter((nombre) => nombre.length <= maximo);

          mostrarSugerencias(unicos);
        } catch (error) {
          // Peticion abortada o sin conexion: no se muestran sugerencias
          ocultarLista();
        }
      }, RETARDO_MS);
    });

    input.addEventListener('keydown', (evento) => {
      if (lista.hidden) return;

      const totalOpciones = lista.querySelectorAll('li').length;

      if (evento.key === 'ArrowDown') {
        evento.preventDefault();
        resaltar((indiceResaltado + 1) % totalOpciones);
      } else if (evento.key === 'ArrowUp') {
        evento.preventDefault();
        resaltar((indiceResaltado - 1 + totalOpciones) % totalOpciones);
      } else if (evento.key === 'Enter') {
        if (indiceResaltado >= 0) {
          evento.preventDefault();
          seleccionar(lista.querySelectorAll('li')[indiceResaltado].textContent);
        }
      } else if (evento.key === 'Escape') {
        ocultarLista();
      }
    });

    input.addEventListener('blur', ocultarLista);
  }

  // Disponible globalmente para inputs creados dinamicamente
  window.inicializarAutocompletadoCiudad = inicializarAutocompletadoCiudad;

  document.addEventListener('DOMContentLoaded', () => {
    document
      .querySelectorAll('input[data-autocompletar-ciudad]')
      .forEach(inicializarAutocompletadoCiudad);
  });
})();
