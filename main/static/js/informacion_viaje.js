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
});