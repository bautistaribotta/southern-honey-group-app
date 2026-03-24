// Lógica para las notificaciones Toast

/**
 * Crea y muestra un nuevo toast dinámicamente
 * @param {string} mensaje - El texto a mostrar
 * @param {string} tipo - 'success', 'error' o 'info'
 */
function crearToast(mensaje, tipo = 'success') {
    const contenedor = document.getElementById('contenedor-toast');
    if (!contenedor) return;

    // Genero el elemento del toast
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;

    // Defino el icono según el tipo de mensaje
    let icono = 'info';
    if (tipo === 'success') icono = 'check_circle';
    if (tipo === 'error') icono = 'error';

    toast.innerHTML = `
        <span class="material-symbols-outlined">${icono}</span>
        <div class="toast-contenido">
            <p>${mensaje}</p>
        </div>
        <button class="btn-cerrar-toast" onclick="cerrarToast(this.parentElement)">
            <span class="material-symbols-outlined">close</span>
        </button>
    `;

    // Lo inserto en el contenedor
    contenedor.appendChild(toast);

    // Configuro el auto-cerrado para que desaparezca en 4 segundos
    setTimeout(() => {
        cerrarToast(toast);
    }, 4000);
}

// Funciones directas para facilitar el uso en otros scripts
function notificarExito(msj) { crearToast(msj, 'success'); }
function notificarError(msj) { crearToast(msj, 'error'); }
function notificarInfo(msj) { crearToast(msj, 'info'); }

/**
 * Cierra un toast con una animación de desvanecimiento
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

// Inicializo los toasts que ya vienen cargados desde el servidor (Django Messages)
function inicializarToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            cerrarToast(toast);
        }, 4000);
    });
}

// Lanzo la inicialización cuando el documento está listo
document.addEventListener('DOMContentLoaded', inicializarToasts);