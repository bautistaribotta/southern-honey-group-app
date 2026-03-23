// Lógica para las notificaciones Toast

/**
 * Cierra un toast con una animación de desvanecimiento
 * @param {HTMLElement} toast - El elemento del toast a cerrar
 */
function cerrarToast(toast) {
    if (!toast) return;
    toast.classList.add('desvanecer');
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 300);
}

//Inicializa los toasts existentes en la página y configura el auto-cerrado
function inicializarToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Auto-cerrar después de 4 segundos (4000 milisegundos)
        setTimeout(() => {
            cerrarToast(toast);
        }, 4000);
    });
}

// Inicializar al cargar el DOM
document.addEventListener('DOMContentLoaded', inicializarToasts);