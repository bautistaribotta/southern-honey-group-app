// Logica de la vista "Informacion del viaje de reparto".
// La eliminacion reutiliza abrirPanelEliminar()/cerrarPanelEliminar() de
// paneles.js (mismo markup #contenedor-panel-eliminar / #boton-confirmar-eliminar)
// y la apertura/cierre del slide-over usa abrirSlideOver()/cerrarSlideOver().
// Aca solo va el alta/baja dinamica de destinos en el panel de edicion.

document.addEventListener('DOMContentLoaded', () => {
    const btnAgregarDestino = document.getElementById('btn-agregar-destino-reparto-editar');
    const btnQuitarDestino = document.getElementById('btn-quitar-destino-reparto-editar');
    const contenedorDestinos = document.getElementById('contenedor-destinos-reparto-editar');

    if (btnAgregarDestino && btnQuitarDestino && contenedorDestinos) {
        const contenedorBotones = btnAgregarDestino.parentElement;

        btnAgregarDestino.addEventListener('click', () => {
            const nuevoInput = document.createElement('input');
            nuevoInput.type = 'text';
            nuevoInput.name = 'destino_reparto';
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
            const inputs = contenedorDestinos.querySelectorAll('input[name="destino_reparto"]');

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
        if (contenedorDestinos.querySelectorAll('input[name="destino_reparto"]').length > 1) {
            btnQuitarDestino.style.display = 'flex';
        }
    }
});
