// Lógica para el manejo de CUIT y facturación
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

// Redirecciono a la vista de detalles del cliente al hacer doble click
function irAInformacionCliente(id) {
    window.location.href = `/informacion_clientes/${id}/`;
}

// Configuro el panel para registrar un cliente nuevo
function prepararPanelNuevo() {
    // Cambio los textos del panel a su estado original
    document.querySelector('#slide-over-panel h3').innerText = 'Nuevo Cliente';
    document.querySelector('#slide-over-panel .texto-cabecera p').innerText = 'Ingrese los datos para el registro';
    document.querySelector('.boton-primario').innerText = 'Guardar Cliente';
    document.querySelector('.icono-contenedor span').innerText = 'person_add';

    // Limpio el formulario y el ID oculto
    document.getElementById('form-cliente').reset();
    document.getElementById('id_cliente').value = '';
    
    // Verifico el estado del campo CUIT y abro el panel
    actualizarCuit();
    abrirPanel();
}

// Configuro el panel con los datos del cliente para editarlo
function prepararPanelEdicion(id) {
    // Pido los datos del cliente al servidor usando su ID
    fetch(`/api/clientes/${id}/`)
        .then(response => response.json())
        .then(cliente => {
            // Actualizo los textos del panel para la edición
            document.querySelector('#slide-over-panel h3').innerText = 'Editar Cliente';
            document.querySelector('#slide-over-panel .texto-cabecera p').innerText = 'Modifique los datos del perfil';
            document.querySelector('.boton-primario').innerText = 'Actualizar Cliente';
            document.querySelector('.icono-contenedor span').innerText = 'edit_note';

            // Relleno los campos del formulario con la información recibida
            document.getElementById('id_cliente').value = cliente.id;
            document.getElementById('nombre').value = cliente.nombre;
            document.getElementById('apellido').value = cliente.apellido;
            document.getElementById('telefono').value = cliente.telefono;
            document.getElementById('localidad').value = cliente.localidad;
            document.getElementById('direccion').value = cliente.direccion;
            document.getElementById('cuit').value = cliente.cuit || '';
            document.getElementById('factura').checked = cliente.factura;

            // Ajusto la visibilidad del CUIT y abro el panel
            actualizarCuit();
            abrirPanel();
        })
        .catch(error => {
            console.error('Error al obtener datos del cliente:', error);
            crearToast('Error al cargar los datos del cliente', 'error');
        });
}

// Manejo los clicks en los botones de la tabla mediante delegación de eventos
document.addEventListener('click', function(e) {
    const botonEditar = e.target.closest('.boton-icono.editar');
    const botonEliminar = e.target.closest('.boton-icono.eliminar');

    if (botonEditar) {
        const id = botonEditar.dataset.id;
        prepararPanelEdicion(id);
    }

    if (botonEliminar) {
        const id = botonEliminar.dataset.id;
        // Aquí implementaré la confirmación de borrado más adelante
    }
});