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