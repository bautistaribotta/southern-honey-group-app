function abrirPanel() {
    document.getElementById('slide-over-contenedor').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarPanel() {
    document.getElementById('slide-over-contenedor').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}

// Lógica para mostrar/ocultar CUIT (Solo si los elementos existen en el HTML actual)
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
    actualizarCuit(); // Ejecutar al cargar
}
