// Modal de "Registrar gasto" del viaje de cereal.
// La eliminacion reutiliza abrirPanelEliminar()/cerrarPanelEliminar() de paneles.js
// (mismo markup #contenedor-panel-eliminar / #boton-confirmar-eliminar).

function abrirModalGasto() {
    document.getElementById('contenedor-modal-gasto').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarModalGasto() {
    document.getElementById('contenedor-modal-gasto').classList.remove('abierto');
    document.body.style.overflow = 'auto';
    const formGasto = document.getElementById('formulario-gasto');
    if (formGasto) {
        formGasto.reset();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Logica para anadir y quitar dinamicamente multiples destinos en el slide-over de edicion
    const btnAgregarDestino = document.getElementById('btn-agregar-destino-cereal');
    const btnQuitarDestino = document.getElementById('btn-quitar-destino-cereal');
    const contenedorDestinos = document.getElementById('contenedor-destinos-cereal');

    if (btnAgregarDestino && btnQuitarDestino && contenedorDestinos) {
        const contenedorBotones = btnAgregarDestino.parentElement;

        btnAgregarDestino.addEventListener('click', () => {
            const nuevoInput = document.createElement('input');
            nuevoInput.type = 'text';
            nuevoInput.name = 'destino';
            nuevoInput.placeholder = 'Siguiente destino...';
            nuevoInput.required = true;
            nuevoInput.maxLength = 30;
            nuevoInput.pattern = '[a-zA-ZÁÉÍÓÚáéíóúñÑ\\s\\d]{3,}';
            nuevoInput.style.marginTop = '0.5rem';

            contenedorDestinos.insertBefore(nuevoInput, contenedorBotones);
            inicializarAutocompletadoCiudad(nuevoInput);

            btnQuitarDestino.style.display = 'flex';
        });

        btnQuitarDestino.addEventListener('click', () => {
            const inputs = contenedorDestinos.querySelectorAll('input[name="destino"]');

            if (inputs.length > 1) {
                const ultimoInput = inputs[inputs.length - 1];
                const listaSugerencias = ultimoInput.nextElementSibling;
                if (listaSugerencias && listaSugerencias.classList.contains('lista-autocompletado-ciudades')) {
                    listaSugerencias.remove();
                }
                contenedorDestinos.removeChild(ultimoInput);
            }

            if (inputs.length - 1 <= 1) {
                btnQuitarDestino.style.display = 'none';
            }
        });

        // Si el viaje ya trae varios destinos cargados, muestro el boton "Quitar"
        if (contenedorDestinos.querySelectorAll('input[name="destino"]').length > 1) {
            btnQuitarDestino.style.display = 'flex';
        }
    }
});
