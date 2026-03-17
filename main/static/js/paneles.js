function abrirPanel() {
    document.getElementById('slide-over-contenedor').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanel() {
    document.getElementById('slide-over-contenedor').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}

// Lógica para Notificaciones Toast
function cerrarToast(toast) {
    toast.classList.add('desvanecer');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

document.addEventListener('DOMContentLoaded', function() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Auto-cerrar después de 4 segundos
        setTimeout(() => {
            if (toast && toast.parentElement) {
                cerrarToast(toast);
            }
        }, 4000);
    });
});
