// Funciones para abrir y cerrar el panel lateral en productos y clientes
/* Estas funciones le agregan o le quitan la clase "slide-over-abierto" al elemento con el id correspondiente */
function abrirSlideOver() {
    document.getElementById('contenedor-slide-over').classList.add('slide-over-abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarSlideOver() {
    document.getElementById('contenedor-slide-over').classList.remove('slide-over-abierto');
    document.body.style.overflow = 'auto';
}

function abrirPanelEliminar() {
    document.getElementById('contenedor-panel-eliminar').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanelEliminar() {
    document.getElementById('contenedor-panel-eliminar').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}

// Lógica para mantener apretado el botón de eliminar durante 3 segundos
document.addEventListener('DOMContentLoaded', () => {
    const btnEliminar = document.getElementById('boton-confirmar-eliminar');
    if (btnEliminar) {
        let timeoutId;
        
        const startHold = (e) => {
            // Solo actuar con el click izquierdo o touch
            if (e.type === 'mousedown' && e.button !== 0) return;
            
            // Prevenir el menú contextual en móviles al mantener presionado
            if (e.type === 'touchstart') {
                e.preventDefault();
            }

            btnEliminar.classList.add('manteniendo');
            
            timeoutId = setTimeout(() => {
                const form = document.getElementById('formulario-eliminar');
                if (form) form.submit();
            }, 2000); // 2 segundos
        };

        const cancelHold = () => {
            btnEliminar.classList.remove('manteniendo');
            clearTimeout(timeoutId);
        };

        // Eventos para Desktop
        btnEliminar.addEventListener('mousedown', startHold);
        btnEliminar.addEventListener('mouseup', cancelHold);
        btnEliminar.addEventListener('mouseleave', cancelHold);
        
        // Eventos para Móviles
        btnEliminar.addEventListener('touchstart', startHold, {passive: false});
        btnEliminar.addEventListener('touchend', cancelHold);
        btnEliminar.addEventListener('touchcancel', cancelHold);
    }
});