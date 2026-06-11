// Redirecciono a la vista de nueva operacion al hacer click
function irANuevaOperacion(id) {
    window.location.href = `/nueva_operacion_venta/${id}/`;
}

// Funciones para el panel de eliminar
function abrirPanelEliminarDesdePerfil(id, nombre) {
    document.getElementById('id_eliminar').value = id;
    document.getElementById('texto-confirmacion-eliminar').innerHTML = `¿Confirma que quiere eliminar al cliente <b>${nombre}</b>?`;

    document.getElementById('contenedor-panel-eliminar').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanelEliminar() {
    document.getElementById('contenedor-panel-eliminar').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}

// =============================================
//  EDICIÓN INLINE DE CLIENTE
// =============================================

document.addEventListener('DOMContentLoaded', () => {
    const btnEditar = document.getElementById('btn-editar-cliente');
    const btnCancelar = document.getElementById('btn-cancelar-edicion');
    const accionesEdicion = document.getElementById('acciones-edicion');
    const valoresVista = document.querySelectorAll('.valor-vista');
    const inputsEdicion = document.querySelectorAll('.input-edicion');
    let editando = false;

    function activarEdicion() {
        editando = true;
        // Ocultar textos, mostrar inputs
        valoresVista.forEach(el => el.style.display = 'none');
        inputsEdicion.forEach(el => el.style.display = '');
        // Mostrar botones guardar/cancelar
        accionesEdicion.style.display = '';
        // Cambiar el botón de editar a estilo activo
        btnEditar.classList.add('activo');
        // Poner borde en la tarjeta
        document.querySelector('.tarjeta-info-unica').classList.add('editando');
    }

    function desactivarEdicion() {
        editando = false;
        // Mostrar textos, ocultar inputs
        valoresVista.forEach(el => el.style.display = '');
        inputsEdicion.forEach(el => el.style.display = 'none');
        // Ocultar botones guardar/cancelar
        accionesEdicion.style.display = 'none';
        // Quitar estilo activo
        btnEditar.classList.remove('activo');
        document.querySelector('.tarjeta-info-unica').classList.remove('editando');
        // Restaurar valores originales en los inputs
        document.getElementById('form-editar-cliente').reset();

        // Al resetear el formulario, el checkbox vuelve a su estado original,
        // pero no dispara el evento 'change'. Fuerzo la actualización aquí
        // para que se remueva el atributo 'required' y desaparezca el error en rojo.
        if (typeof actualizarRequiredCuit === 'function') {
            actualizarRequiredCuit();
        }
    }

    btnEditar.addEventListener('click', () => {
        if (editando) {
            desactivarEdicion();
        } else {
            activarEdicion();
        }
    });

    btnCancelar.addEventListener('click', () => {
        desactivarEdicion();
    });

    // CUIT obligatorio si factura la producción
    const checkFactura = document.querySelector('input[name="factura"]');
    const inputCuit = document.querySelector('input[name="cuit"].input-edicion');

    function actualizarRequiredCuit() {
        if (checkFactura.checked) {
            inputCuit.required = true;
        } else {
            inputCuit.required = false;
            inputCuit.value = '';
        }
    }

    checkFactura.addEventListener('change', actualizarRequiredCuit);
    // Aplicar estado inicial
    actualizarRequiredCuit();

    // Autocapitalizar la primera letra al escribir en campos de nombre y apellido
    const inputsNombres = document.querySelectorAll('input[name="nombre"], input[name="apellido"]');
    inputsNombres.forEach(input => {
        input.addEventListener('input', (e) => {
            let valor = e.target.value;
            if (valor.length > 0) {
                e.target.value = valor.charAt(0).toUpperCase() + valor.slice(1);
            }
        });
    });

    // Lógica para mantener apretado el botón de eliminar durante 2 segundos
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
                const form = document.getElementById('formulario-eliminar');
                if (form) form.submit();
            }, 2000); // 2 segundos
        };

        const cancelHold = () => {
            btnEliminar.classList.remove('manteniendo');
            const span = btnEliminar.querySelector('span');
            if (span && btnEliminar.dataset.textoOriginal) {
                span.innerText = btnEliminar.dataset.textoOriginal;
            }
            clearTimeout(timeoutId);
        };

        btnEliminar.addEventListener('mousedown', startHold);
        btnEliminar.addEventListener('mouseup', cancelHold);
        btnEliminar.addEventListener('mouseleave', cancelHold);
        btnEliminar.addEventListener('touchstart', startHold, {passive: false});
        btnEliminar.addEventListener('touchend', cancelHold);
        btnEliminar.addEventListener('touchcancel', cancelHold);
    }

    // Permitir solo números en los campos Teléfono y CUIT
    const inputTelefono = document.querySelector('input[name="telefono"].input-edicion');
    if (inputTelefono) {
        inputTelefono.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    if (inputCuit) {
        inputCuit.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');

            // Si el usuario escribe algo y el switch de factura está apagado, lo enciendo automáticamente
            if (e.target.value.length > 0 && checkFactura && !checkFactura.checked) {
                checkFactura.checked = true;
                // Actualizo el atributo 'required' llamando a la función
                actualizarRequiredCuit();
            }
        });
    }
});
