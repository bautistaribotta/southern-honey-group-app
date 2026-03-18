// Funciones para abrir y cerrar el panel lateral en productos y clientes
function abrirPanel() {
    document.getElementById('slide-over-contenedor').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanel() {
    document.getElementById('slide-over-contenedor').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}