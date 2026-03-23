// Lógica para las notificaciones Toast

/**
 * Crea y muestra un nuevo toast dinámicamente
 * @param {string} mensaje - El texto a mostrar
 * @param {string} tipo - 'success', 'error' o 'info'
 */
function crearToast(mensaje, tipo = 'success') {
    const contenedor = document.getElementById('contenedor-toast');
    if (!contenedor) return;

    // Crear el elemento toast
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;

    // Determinar el icono según el tipo
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

    // Añadir al contenedor
    contenedor.appendChild(toast);

    // Auto-cerrar después de 4 segundos
    setTimeout(() => {
        cerrarToast(toast);
    }, 4000);
}

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

// Inicializa los toasts existentes en la página y configura el auto-cerrado
function inicializarToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Auto-cerrar después de 4 segundos
        setTimeout(() => {
            cerrarToast(toast);
        }, 4000);
    });
}

// Inicializar al cargar el DOM
document.addEventListener('DOMContentLoaded', inicializarToasts);