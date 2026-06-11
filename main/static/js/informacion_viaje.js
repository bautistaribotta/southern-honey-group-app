function abrirModalEliminarViaje() {
    document.getElementById('contenedor-panel-eliminar').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarModalEliminarViaje() {
    document.getElementById('contenedor-panel-eliminar').classList.remove('abierto');
    document.body.style.overflow = 'auto';
    
    const btnEliminar = document.getElementById('boton-confirmar-eliminar');
    if (btnEliminar) {
        btnEliminar.classList.remove('manteniendo');
        const span = btnEliminar.querySelector('span');
        if (span && btnEliminar.dataset.textoOriginal) {
            span.innerText = btnEliminar.dataset.textoOriginal;
        }
    }
}

function abrirModalGasto() {
    document.getElementById('contenedor-modal-gasto').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarModalGasto() {
    document.getElementById('contenedor-modal-gasto').classList.remove('abierto');
    document.body.style.overflow = 'auto';
    // Opcional: Resetear el formulario de gasto al cerrarlo
    const formGasto = document.getElementById('formulario-gasto');
    if (formGasto) {
        formGasto.reset();
    }
}

// Tipo de operacion elegido al abrir el modal de seleccion de cliente ('venta' | 'compra')
let tipoOperacionSeleccionada = 'venta';

// Elemento que tenia el foco antes de abrir el modal, para restaurarlo al cerrar
let elementoFocoPrevio = null;
// Indice de la opcion resaltada dentro de las visibles (-1 = ninguna)
let indiceClienteResaltado = -1;

function abrirModalSeleccionCliente(tipo) {
    tipoOperacionSeleccionada = tipo;
    elementoFocoPrevio = document.activeElement;

    const titulo = document.getElementById('titulo-modal-cliente');
    if (titulo) {
        titulo.innerText = tipo === 'compra'
            ? 'Seleccionar cliente para la compra'
            : 'Seleccionar cliente para la venta';
    }

    document.getElementById('contenedor-modal-cliente').classList.add('abierto');
    document.body.style.overflow = 'hidden';

    const input = document.getElementById('input-buscar-cliente');
    if (input) {
        input.value = '';
        filtrarClientesModal();
        input.focus();
    }
}

function cerrarModalSeleccionCliente() {
    document.getElementById('contenedor-modal-cliente').classList.remove('abierto');
    document.body.style.overflow = 'auto';

    // Devuelvo el foco al boton que abrio el modal
    if (elementoFocoPrevio && typeof elementoFocoPrevio.focus === 'function') {
        elementoFocoPrevio.focus();
    }
    elementoFocoPrevio = null;
}

// Devuelve las opciones de cliente actualmente visibles
function clientesVisiblesModal() {
    return Array.from(document.querySelectorAll('#lista-clientes-modal .item-cliente-modal'))
        .filter(item => !item.hidden);
}

// Resalta la opcion en el indice dado y la expone via aria-activedescendant
function resaltarClienteModal(indice) {
    const input = document.getElementById('input-buscar-cliente');
    const visibles = clientesVisiblesModal();

    document.querySelectorAll('#lista-clientes-modal .item-cliente-modal').forEach(item => {
        item.classList.remove('resaltado');
        item.setAttribute('aria-selected', 'false');
    });

    if (indice < 0 || indice >= visibles.length) {
        indiceClienteResaltado = -1;
        if (input) input.setAttribute('aria-activedescendant', '');
        return;
    }

    const item = visibles[indice];
    item.classList.add('resaltado');
    item.setAttribute('aria-selected', 'true');
    item.scrollIntoView({ block: 'nearest' });
    if (input) input.setAttribute('aria-activedescendant', item.id);
    indiceClienteResaltado = indice;
}

// Filtra la lista de clientes del modal por nombre o apellido
function filtrarClientesModal() {
    const campo = document.getElementById('input-buscar-cliente');
    const termino = (campo ? campo.value : '').trim().toLowerCase();
    const items = document.querySelectorAll('#lista-clientes-modal .item-cliente-modal');

    let visibles = 0;
    items.forEach(item => {
        const coincide = item.dataset.nombre.includes(termino);
        item.hidden = !coincide;
        if (coincide) visibles++;
    });

    const sinResultados = document.getElementById('sin-resultados-cliente');
    if (sinResultados) {
        sinResultados.hidden = visibles !== 0;
    }

    // Al cambiar el filtro reseteo el resaltado
    resaltarClienteModal(-1);
}

// Navega a la operacion del cliente elegido
function elegirClienteModal(item) {
    if (!item) return;
    const idCliente = item.dataset.id;
    const idViaje = obtenerIdViaje();
    const base = tipoOperacionSeleccionada === 'compra' ? 'nueva_operacion_compra' : 'nueva_operacion_venta';
    window.location.href = `/${base}/${idCliente}/?viaje=${idViaje}`;
}

// Extrae el id del viaje desde la URL /informacion_viaje/<id>/
function obtenerIdViaje() {
    const coincidencia = window.location.pathname.match(/informacion_viaje\/(\d+)/);
    return coincidencia ? coincidencia[1] : '';
}

document.addEventListener('DOMContentLoaded', () => {
    const btnEliminar = document.getElementById('boton-confirmar-eliminar');
    if (btnEliminar) {
        let timeoutId;
        
        const startHold = (e) => {
            if (e.type === 'mousedown' && e.button !== 0) return;
            if (e.type === 'touchstart') e.preventDefault();

            btnEliminar.classList.add('manteniendo');
            const span = btnEliminar.querySelector('span');
            if (span) {
                if (!btnEliminar.dataset.textoOriginal) {
                    btnEliminar.dataset.textoOriginal = span.innerText;
                }
                span.innerText = "Mantenga presionado...";
            }
            
            timeoutId = setTimeout(() => {
                document.getElementById('formulario-eliminar').submit();
            }, 2000); // 2 segundos
        };

        const stopHold = () => {
            clearTimeout(timeoutId);
            btnEliminar.classList.remove('manteniendo');
            const span = btnEliminar.querySelector('span');
            if (span && btnEliminar.dataset.textoOriginal) {
                span.innerText = btnEliminar.dataset.textoOriginal;
            }
        };

        btnEliminar.addEventListener('mousedown', startHold);
        btnEliminar.addEventListener('touchstart', startHold, {passive: false});
        btnEliminar.addEventListener('mouseup', stopHold);
        btnEliminar.addEventListener('mouseleave', stopHold);
        btnEliminar.addEventListener('touchend', stopHold);
        btnEliminar.addEventListener('touchcancel', stopHold);
    }

    // Lógica para añadir y quitar dinámicamente múltiples destinos en el slide-over
    const btnAgregarDestino = document.getElementById('btn-agregar-destino');
    const btnQuitarDestino = document.getElementById('btn-quitar-destino');
    const contenedorDestinos = document.getElementById('contenedor-destinos');

    if (btnAgregarDestino && btnQuitarDestino && contenedorDestinos) {
        const contenedorBotones = btnAgregarDestino.parentElement;

        // Evento Agregar
        btnAgregarDestino.addEventListener('click', () => {
            const nuevoInput = document.createElement('input');
            nuevoInput.type = 'text';
            nuevoInput.name = 'destino';
            nuevoInput.placeholder = 'Siguiente destino...';
            nuevoInput.required = true;
            nuevoInput.maxLength = 30;
            nuevoInput.pattern = '[a-zA-ZÁÉÍÓÚáéíóúñÑ\\s\\d]{3,}';
            nuevoInput.style.marginTop = '0.5rem';

            // Insertamos el nuevo input antes de los botones
            contenedorDestinos.insertBefore(nuevoInput, contenedorBotones);
            inicializarAutocompletadoCiudad(nuevoInput);

            // Mostrar el botón de quitar porque ahora hay más de un input
            btnQuitarDestino.style.display = 'flex';
        });

        // Evento Quitar
        btnQuitarDestino.addEventListener('click', () => {
            const inputs = contenedorDestinos.querySelectorAll('input[name="destino"]');
            
            if (inputs.length > 1) {
                // Elimina el último input y su lista de sugerencias asociada
                const ultimoInput = inputs[inputs.length - 1];
                const listaSugerencias = ultimoInput.nextElementSibling;
                if (listaSugerencias && listaSugerencias.classList.contains('lista-autocompletado-ciudades')) {
                    listaSugerencias.remove();
                }
                contenedorDestinos.removeChild(ultimoInput);
            }

            // Si después de eliminar queda solo 1, oculto el botón "Quitar"
            if (inputs.length - 1 <= 1) {
                btnQuitarDestino.style.display = 'none';
            }
        });
    }

    // Modal de seleccion de cliente: buscador y navegacion al carrito
    const inputBuscarCliente = document.getElementById('input-buscar-cliente');
    if (inputBuscarCliente) {
        inputBuscarCliente.addEventListener('input', filtrarClientesModal);

        // Navegacion por teclado de la lista desde el buscador (patron combobox)
        inputBuscarCliente.addEventListener('keydown', (evento) => {
            const visibles = clientesVisiblesModal();

            if (evento.key === 'ArrowDown') {
                evento.preventDefault();
                if (visibles.length === 0) return;
                resaltarClienteModal((indiceClienteResaltado + 1) % visibles.length);
            } else if (evento.key === 'ArrowUp') {
                evento.preventDefault();
                if (visibles.length === 0) return;
                resaltarClienteModal((indiceClienteResaltado - 1 + visibles.length) % visibles.length);
            } else if (evento.key === 'Enter') {
                evento.preventDefault();
                if (indiceClienteResaltado >= 0) {
                    elegirClienteModal(visibles[indiceClienteResaltado]);
                } else if (visibles.length === 1) {
                    // Un solo resultado: lo elijo directamente
                    elegirClienteModal(visibles[0]);
                }
            }
        });
    }

    document.querySelectorAll('#lista-clientes-modal .item-cliente-modal').forEach(item => {
        item.addEventListener('click', () => elegirClienteModal(item));
        // Resalto al pasar el mouse para mantener sincronizado el estado visual
        item.addEventListener('mousemove', () => {
            const visibles = clientesVisiblesModal();
            const indice = visibles.indexOf(item);
            if (indice !== -1 && indice !== indiceClienteResaltado) {
                resaltarClienteModal(indice);
            }
        });
    });

    // Cierro el modal con Escape y atrapo el foco con Tab mientras esta abierto
    const contenedorModalCliente = document.getElementById('contenedor-modal-cliente');
    if (contenedorModalCliente) {
        contenedorModalCliente.addEventListener('keydown', (evento) => {
            if (!contenedorModalCliente.classList.contains('abierto')) return;

            if (evento.key === 'Escape') {
                evento.preventDefault();
                cerrarModalSeleccionCliente();
                return;
            }

            if (evento.key === 'Tab') {
                const panel = document.getElementById('panel-cliente');
                const focusables = panel.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                const visibles = Array.from(focusables).filter(el => !el.disabled && el.offsetParent !== null);
                if (visibles.length === 0) return;

                const primero = visibles[0];
                const ultimo = visibles[visibles.length - 1];

                if (evento.shiftKey && document.activeElement === primero) {
                    evento.preventDefault();
                    ultimo.focus();
                } else if (!evento.shiftKey && document.activeElement === ultimo) {
                    evento.preventDefault();
                    primero.focus();
                }
            }
        });
    }
});