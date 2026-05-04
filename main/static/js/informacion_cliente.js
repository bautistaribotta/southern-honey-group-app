// Redirecciono a la vista de nueva operacion al hacer click
function irANuevaOperacion(id) {
    window.location.href = `/operaciones/${id}/`;
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

// Función para abrir el modal de cancelar operación
function abrirModalCancelarOperacion(id) {
    const modal = document.getElementById('contenedor-modal-cancelar');
    const btnConfirmar = document.getElementById('boton-confirmar-cancelar');
    const textoConfirmacion = document.getElementById('texto-confirmacion-cancelar');
    
    // Inyectamos el ID de la operación en el texto
    textoConfirmacion.innerHTML = `¿Seguro que quiere cancelar la operacion <b>#${id}</b>? Los productos seran devueltos al stock automaticamente`;
    
    // Guardamos el ID en el botón para saber qué operación cancelar
    btnConfirmar.setAttribute('data-id', id);
    
    modal.classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

// Función para cerrar el modal de cancelar operación
function cerrarModalCancelarOperacion() {
    const modal = document.getElementById('contenedor-modal-cancelar');
    const btnConfirmar = document.getElementById('boton-confirmar-cancelar');
    
    modal.classList.remove('abierto');
    document.body.style.overflow = 'auto';
    
    // Limpiamos el estado del botón
    btnConfirmar.classList.remove('manteniendo');
    const span = btnConfirmar.querySelector('span');
    if (span && btnConfirmar.dataset.textoOriginal) {
        span.innerText = btnConfirmar.dataset.textoOriginal;
    }
}

// Lógica de "mantener" para el botón de cancelar operación
document.addEventListener('DOMContentLoaded', () => {
    const btnConfirmarCancelar = document.getElementById('boton-confirmar-cancelar');
    if (btnConfirmarCancelar) {
        let timeoutId;
        
        const startHold = (e) => {
            if (e.type === 'mousedown' && e.button !== 0) return;
            // No prevenimos default en touch para permitir scroll si fuera necesario, 
            // pero aquí como es un modal fijo, podemos ser más estrictos
            if (e.type === 'touchstart') e.preventDefault();

            btnConfirmarCancelar.classList.add('manteniendo');
            const span = btnConfirmarCancelar.querySelector('span');
            if (span) {
                if (!btnConfirmarCancelar.dataset.textoOriginal) {
                    btnConfirmarCancelar.dataset.textoOriginal = span.innerText;
                }
                span.innerText = "Mantenga presionado...";
            }
            
            timeoutId = setTimeout(() => {
                const id = btnConfirmarCancelar.getAttribute('data-id');
                ejecutarCancelacionOperacion(id);
            }, 2000); // 2 segundos
        };

        const cancelHold = () => {
            btnConfirmarCancelar.classList.remove('manteniendo');
            const span = btnConfirmarCancelar.querySelector('span');
            if (span && btnConfirmarCancelar.dataset.textoOriginal) {
                span.innerText = btnConfirmarCancelar.dataset.textoOriginal;
            }
            clearTimeout(timeoutId);
        };

        btnConfirmarCancelar.addEventListener('mousedown', startHold);
        btnConfirmarCancelar.addEventListener('mouseup', cancelHold);
        btnConfirmarCancelar.addEventListener('mouseleave', cancelHold);
        btnConfirmarCancelar.addEventListener('touchstart', startHold, {passive: false});
        btnConfirmarCancelar.addEventListener('touchend', cancelHold);
        btnConfirmarCancelar.addEventListener('touchcancel', cancelHold);
    }
    
    // ... (resto del DOMContentLoaded existente)
});

// Función que realiza la petición AJAX final
async function ejecutarCancelacionOperacion(id) {
    try {
        const response = await fetch(`/cancelar_operacion/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json().catch(() => ({}));
            if (typeof notificarError === 'function') {
                notificarError(data.error || "Hubo un error al cancelar la operación.");
            } else {
                alert(data.error || "Hubo un error al cancelar la operación.");
            }
            cerrarModalCancelarOperacion();
        }
    } catch (error) {
        console.error("Error:", error);
        if (typeof notificarError === 'function') {
            notificarError("Ocurrió un error inesperado al cancelar la operación.");
        } else {
            alert("Ocurrió un error inesperado al cancelar la operación.");
        }
        cerrarModalCancelarOperacion();
    }
}

// Función auxiliar para obtener el CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// =============================================
//  MODAL AÑADIR PAGO
// =============================================

function abrirModalPago(idOperacion, montoTotalStr, totalPagadoStr) {
    // Reemplazamos coma por punto para float en caso de que venga con formato regional
    const montoTotal = parseFloat(montoTotalStr.replace(',', '.')) || 0;
    const totalPagado = parseFloat(totalPagadoStr.replace(',', '.')) || 0;
    const restante = montoTotal - totalPagado;
    
    document.getElementById('id_operacion_pago').value = idOperacion;
    
    document.getElementById('titulo-modal-pago').innerHTML = `Añadir pago a la operación <b>#${idOperacion}</b>`;
    
    // Formatear a 2 decimales para mostrar
    document.getElementById('monto-restante-pago').textContent = `$${restante.toFixed(2)}`;
    
    const inputMonto = document.getElementById('input-monto-pago');
    inputMonto.value = '';
    // Guardamos el máximo permitido (se usa en la validación)
    inputMonto.max = restante.toFixed(2);
    
    const modal = document.getElementById('contenedor-modal-pago');
    modal.classList.add('abierto');
    document.body.style.overflow = 'hidden';
    
    // Enfocar el input después de que se abra el modal
    setTimeout(() => {
        inputMonto.focus();
    }, 100);
}

function completarPagoTotal() {
    const inputMonto = document.getElementById('input-monto-pago');
    if (inputMonto && inputMonto.max) {
        inputMonto.value = inputMonto.max;
        inputMonto.focus();
    }
}

function cerrarModalPago() {
    const modal = document.getElementById('contenedor-modal-pago');
    modal.classList.remove('abierto');
    document.body.style.overflow = 'auto';
}

function procesarPago() {
    const idOperacion = document.getElementById('id_operacion_pago').value;
    const monto = document.getElementById('input-monto-pago').value;
    const maxPermitido = document.getElementById('input-monto-pago').max;
    
    if (!monto || isNaN(monto) || parseFloat(monto) <= 0) {
        if (typeof notificarError === 'function') notificarError("Ingrese un monto válido.");
        else alert("Ingrese un monto válido.");
        return;
    }
    
    // Redondeamos ambos a 2 decimales para evitar problemas de precisión float
    const montoNum = Math.round(parseFloat(monto) * 100) / 100;
    const maxNum = Math.round(parseFloat(maxPermitido) * 100) / 100;
    
    if (montoNum > maxNum) {
        const err = `El monto no puede superar el restante a pagar ($${maxNum.toFixed(2)}).`;
        if (typeof notificarError === 'function') notificarError(err);
        else alert(err);
        return;
    }
    
    const btn = document.getElementById('boton-confirmar-pago');
    btn.disabled = true;
    const spanOriginal = btn.innerHTML;
    btn.innerHTML = '<span>Procesando...</span>';
    
    fetch(`/registrar_pago/${idOperacion}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ monto: monto })
    })
    .then(response => response.json())
    .then(data => {
        if(data.ok) {
            cerrarModalPago();
            window.location.reload(); 
        } else {
            const err = data.error || "Hubo un error al registrar el pago.";
            if (typeof notificarError === 'function') notificarError(err);
            else alert(err);
            btn.disabled = false;
            btn.innerHTML = spanOriginal;
        }
    })
    .catch(err => {
        console.error("Error al procesar pago:", err);
        const msg = "Error de conexión. Intente nuevamente.";
        if (typeof notificarError === 'function') notificarError(msg);
        else alert(msg);
        btn.disabled = false;
        btn.innerHTML = spanOriginal;
    });
}