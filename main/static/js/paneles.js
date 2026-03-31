// Funciones para abrir y cerrar el panel lateral en productos y clientes
/* Estas funciones le agregan o le quitan la clase "abierto" al elemento con el id correspondiente */
function abrirPanelSlideOver() {
    document.getElementById('slide-over-contenedor').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanelSlideOver() {
    document.getElementById('slide-over-contenedor').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}

function abrirPanelEliminar() {
    document.getElementById('panel-eliminar-contenedor').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanelEliminar() {
    document.getElementById('panel-eliminar-contenedor').classList.remove('cerrado');
    document.body.style.overflow = 'auto';
}