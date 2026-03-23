// Codigo para la logica del CUIT
const checkboxFactura = document.getElementById('factura');
const campoCuit = document.getElementById('campo-cuit');

if (checkboxFactura && campoCuit) {
    function actualizarCuit() {
        if (checkboxFactura.checked) {
            campoCuit.style.display = 'flex';
        } else {
            campoCuit.style.display = 'none';
        }
    }
    
    checkboxFactura.addEventListener('change', actualizarCuit);
    actualizarCuit(); 
}

// Redirección al hacer doble click en la fila
function irAInformacionCliente(id) {
    // Redirige a la vista de información pasándole el ID como parámetro (si tu vista lo espera así)
    // O simplemente a la página si es una página estática por ahora
    window.location.href = `/informacion_clientes?id=${id}`;
}

// Delegación de eventos para botones de la tabla (útil para cuando la tabla se recarga por AJAX)
document.addEventListener('click', function(e) {
    const botonEditar = e.target.closest('.boton-icono.editar');
    const botonEliminar = e.target.closest('.boton-icono.eliminar');

    if (botonEditar) {
        const id = botonEditar.dataset.id;
    }

    if (botonEliminar) {
        const id = botonEliminar.dataset.id;
    }
});