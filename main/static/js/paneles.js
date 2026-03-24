// Funciones para abrir y cerrar el panel lateral en productos y clientes
/* Estas funciones le agregan o le quitan la clase "abierto" al elemento con el id de "slide-over-contenedor" */
function abrirPanel() {
    document.getElementById('slide-over-contenedor').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanel() {
    document.getElementById('slide-over-contenedor').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}