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

            // Mostrar el botón de quitar porque ahora hay más de un input
            btnQuitarDestino.style.display = 'flex';
        });

        // Evento Quitar
        btnQuitarDestino.addEventListener('click', () => {
            const inputs = contenedorDestinos.querySelectorAll('input[name="destino"]');
            
            if (inputs.length > 1) {
                // Elimina el último input
                contenedorDestinos.removeChild(inputs[inputs.length - 1]);
            }

            // Si después de eliminar queda solo 1, oculto el botón "Quitar"
            if (inputs.length - 1 <= 1) {
                btnQuitarDestino.style.display = 'none';
            }
        });
    }
});