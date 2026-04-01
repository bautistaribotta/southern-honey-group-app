function prepararPanelNuevoProducto() {
    // Restauro los textos originales para el registro de un nuevo producto
    document.querySelector('#slide-over-panel h3').innerText = 'Nuevo Producto';
    document.querySelector('#slide-over-panel .texto-cabecera p').innerText = 'Complete los detalles para el inventario';
    document.querySelector('.boton-primario').innerText = 'Guardar Producto';
    document.querySelector('.icono-contenedor span').innerText = 'inventory_2';

    // Limpio el formulario y el ID oculto para evitar ediciones accidentales
    document.getElementById('form-producto').reset();
    document.getElementById('id_producto').value = '';
    
    abrirPanel();
}

function prepararPanelEditarProducto(id) {
    // Pido los datos del producto al servidor mediante la nueva API que creamos
    fetch(`/api/productos/${id}/`)
        .then(response => response.json())
        .then(producto => {
            // Actualizo los textos del panel slide-over para reflejar que estamos editando
            document.querySelector('#slide-over-panel h3').innerText = 'Editar Producto';
            document.querySelector('#slide-over-panel .texto-cabecera p').innerText = 'Modifique los datos del producto';
            document.querySelector('.boton-primario').innerText = 'Actualizar Producto';
            
            // Uso el icono 'edit_square' que es moderno y claro para la edición
            document.querySelector('.icono-contenedor span').innerText = 'edit_square';

            // Relleno los campos del formulario con la información real del producto
            document.getElementById('id_producto').value = producto.id;
            document.getElementById('nombre').value = producto.nombre;
            document.getElementById('categoria').value = producto.categoria;
            document.getElementById('precio').value = producto.precio;
            document.getElementById('stock').value = producto.cantidad;

            // Abro el panel una vez que los datos están cargados
            abrirPanel();
        })
        .catch(error => {
            console.error('Error al obtener datos del producto:', error);
            // Si existe la función de notificaciones, aviso del error
            if (typeof crearToast === 'function') {
                crearToast('Error al cargar los datos del producto', 'error');
            }
        });
}

// Configuro la delegación de eventos para capturar los clicks en los botones de la tabla
document.addEventListener('click', function(e) {
    // Busco el botón de editar más cercano al elemento clickeado
    const botonEditar = e.target.closest('.boton-icono.editar');

    if (botonEditar) {
        // Extraigo el ID del atributo data-id que definimos en el HTML
        const id = botonEditar.dataset.id;
        prepararPanelEditarProducto(id);
    }
});