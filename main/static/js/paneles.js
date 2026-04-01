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
    document.getElementById('panel-eliminar-contenedor').classList.add('panel-abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanelEliminar() {
    document.getElementById('panel-eliminar-contenedor').classList.remove('panel-abierto');
    document.body.style.overflow = 'auto';
}