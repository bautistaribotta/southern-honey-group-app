document.addEventListener('DOMContentLoaded', () => {
    const cuerpoCarrito = document.getElementById('cuerpo-carrito');
    const elementoTotal = document.querySelector('.total-destacado');
    const inputBusqueda = document.querySelector('.input-busqueda');
    const contenedorTabla = document.getElementById('contenedor-tabla-operaciones');

    // Clave en sessionStorage para persistir el carrito
    const STORAGE_KEY = 'carrito_operacion';

    // =============================================
    //  PERSISTENCIA DEL CARRITO (sessionStorage)
    // =============================================

    function guardarCarrito() {
        const filas = cuerpoCarrito.querySelectorAll('tr');
        const items = [];
        filas.forEach(fila => {
            items.push({
                id: fila.dataset.id,
                precio: fila.dataset.precio,
                nombre: fila.querySelector('.item-nombre').textContent,
                cantidad: parseInt(fila.querySelector('.input-cantidad').value),
                stockOriginal: parseInt(fila.dataset.stockOriginal)
            });
        });
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    }

    function restaurarCarrito() {
        // Detectar si la página fue recargada (F5) o es una navegación nueva
        const navegacion = performance.getEntriesByType('navigation')[0];
        const esRecarga = navegacion && navegacion.type === 'reload';

        if (!esRecarga) {
            // Es una navegación nueva (ej: volver al perfil y entrar de nuevo)
            // → limpiar cualquier carrito viejo
            sessionStorage.removeItem(STORAGE_KEY);
            return;
        }

        const datos = sessionStorage.getItem(STORAGE_KEY);
        if (!datos) return;

        const items = JSON.parse(datos);
        items.forEach(item => {
            crearFilaCarrito(
                item.id,
                item.nombre,
                parseFloat(item.precio),
                item.cantidad,
                item.stockOriginal
            );
        });
        actualizarTotal();
        // Ajustar el stock visual de los productos visibles en la tabla
        ajustarStockVisual();
    }

    /** Limpia el carrito del storage */
    function limpiarCarritoStorage() {
        sessionStorage.removeItem(STORAGE_KEY);
    }

    // =============================================
    //  CONTROL DE STOCK VISUAL
    // =============================================

    /**
     * Busca la fila del producto en la tabla de listado por su ID.
     * Retorna { fila, stockCell, boton } o null si el producto no está en la página actual.
     */
    function buscarProductoEnTabla(idProducto) {
        const boton = contenedorTabla.querySelector(`.boton-agregar-producto[data-id="${idProducto}"]`);
        if (!boton) return null;

        const fila = boton.closest('tr');
        const stockCell = fila.querySelector('.stock-valor');
        return { fila, stockCell, boton };
    }

    /**
     * Actualiza el stock visual de un producto en la tabla de listado.
     * Cambia el número mostrado y deshabilita el botón si el stock llega a 0.
     */
    function actualizarStockProducto(idProducto, stockDisponible) {
        const producto = buscarProductoEnTabla(idProducto);
        if (!producto) return;

        producto.stockCell.textContent = stockDisponible;

        if (stockDisponible <= 0) {
            producto.boton.disabled = true;
            producto.boton.classList.add('boton-sin-stock');
        } else {
            producto.boton.disabled = false;
            producto.boton.classList.remove('boton-sin-stock');
        }
    }

    /**
     * Recorre los items del carrito y ajusta el stock visual de los productos
     * que estén visibles en la tabla de listado.
     */
    function ajustarStockVisual() {
        const filasCarrito = cuerpoCarrito.querySelectorAll('tr');
        filasCarrito.forEach(filaCarrito => {
            const idProducto = filaCarrito.dataset.id;
            const cantidadEnCarrito = parseInt(filaCarrito.querySelector('.input-cantidad').value);
            const stockOriginal = parseInt(filaCarrito.dataset.stockOriginal);
            const stockDisponible = stockOriginal - cantidadEnCarrito;

            actualizarStockProducto(idProducto, stockDisponible);
        });
    }

    // =============================================
    //  LÓGICA DEL CARRITO
    // =============================================

    /**
     * Vincula los botones de "agregar al carrito" de la tabla de productos.
     * Se debe llamar cada vez que se reemplaza el contenido de la tabla (AJAX).
     */
    function vincularBotonesAgregar() {
        const botones = contenedorTabla.querySelectorAll('.boton-agregar-producto');
        botones.forEach(boton => {
            boton.addEventListener('click', function () {
                const id = this.dataset.id;
                const nombre = this.dataset.nombre;
                const precioStr = this.dataset.precio;
                const precio = parseFloat(precioStr.replace(',', '.'));
                const stockOriginal = parseInt(this.dataset.stock);

                agregarAlCarrito(id, nombre, precio, stockOriginal);
            });
        });
    }

    function agregarAlCarrito(id, nombre, precio, stockOriginal) {
        const filaExistente = cuerpoCarrito.querySelector(`tr[data-id="${id}"]`);

        if (filaExistente) {
            const inputCantidad = filaExistente.querySelector('.input-cantidad');
            const cantidadActual = parseInt(inputCantidad.value);

            // Validar que no supere el stock original
            if (cantidadActual >= stockOriginal) {
                return;
            }

            inputCantidad.value = cantidadActual + 1;
            actualizarStockProducto(id, stockOriginal - (cantidadActual + 1));
        } else {
            if (stockOriginal <= 0) {
                return;
            }

            crearFilaCarrito(id, nombre, precio, 1, stockOriginal);
            actualizarStockProducto(id, stockOriginal - 1);
        }

        actualizarTotal();
        guardarCarrito();
    }

    function crearFilaCarrito(id, nombre, precio, cantidad, stockOriginal) {
        const fila = document.createElement('tr');
        fila.dataset.id = id;
        fila.dataset.precio = precio;
        fila.dataset.stockOriginal = stockOriginal;

        fila.innerHTML = `
            <td class="texto-centrado">
                <input type="number" class="input-cantidad" value="${cantidad}" min="1" max="${stockOriginal}">
            </td>
            <td>
                <div class="item-nombre" title="${nombre}">${nombre}</div>
                <div class="item-precio">$ ${precio.toFixed(2)} c/u</div>
            </td>
            <td class="texto-derecha">
                <button type="button" class="boton-eliminar-item"><span class="material-symbols-outlined">delete</span></button>
            </td>
        `;

        // Recalcular el total y validar stock cuando el usuario cambia la cantidad
        const inputCantidad = fila.querySelector('.input-cantidad');

        inputCantidad.addEventListener('input', function () {
            let val = parseInt(this.value);

            if (isNaN(val) || val < 1) {
                val = 1;
                this.value = 1;
            }

            if (val > stockOriginal) {
                val = stockOriginal;
                this.value = stockOriginal;
            }

            const stockDisponible = stockOriginal - val;
            actualizarStockProducto(id, stockDisponible);

            actualizarTotal();
            guardarCarrito();
        });

        // Lógica para restar de a 1 y eliminar la fila si llega a 0
        const botonEliminar = fila.querySelector('.boton-eliminar-item');
        botonEliminar.addEventListener('click', function () {
            const cantidadActual = parseInt(inputCantidad.value);

            if (cantidadActual > 1) {
                // Restar 1 a la cantidad
                inputCantidad.value = cantidadActual - 1;
                actualizarStockProducto(id, stockOriginal - (cantidadActual - 1));
            } else {
                // Cantidad es 1 → eliminar la fila y restaurar todo el stock
                fila.remove();
                actualizarStockProducto(id, stockOriginal);
            }

            actualizarTotal();
            guardarCarrito();
        });

        cuerpoCarrito.appendChild(fila);
    }

    function actualizarTotal() {
        let total = 0;
        const filasCarrito = cuerpoCarrito.querySelectorAll('tr');

        filasCarrito.forEach(fila => {
            const precio = parseFloat(fila.dataset.precio);
            const cantidad = parseInt(fila.querySelector('.input-cantidad').value);
            total += precio * cantidad;
        });

        elementoTotal.textContent = `$ ${total.toFixed(2)}`;
    }

    // =============================================
    //  BUSCADOR DE PRODUCTOS (AJAX)
    // =============================================

    let timeoutBusqueda = null;

    /**
     * Realiza una búsqueda AJAX y reemplaza solo el contenido de la tabla.
     * @param {string|null} urlString - URL opcional (ej: para paginación)
     */
    function buscarProductos(urlString = null) {
        let url;

        if (urlString) {
            url = new URL(urlString, window.location.origin);
        } else {
            url = new URL(window.location.href);
            url.searchParams.set('q', inputBusqueda.value.trim());
            url.searchParams.delete('page');
        }

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(response => response.text())
            .then(html => {
                contenedorTabla.innerHTML = html;
                // Re-vincular los botones de agregar y paginación tras reemplazar el HTML
                vincularBotonesAgregar();
                vincularPaginacion();
                // Ajustar stock visual según el carrito actual
                ajustarStockVisual();
            })
            .catch(error => console.error('Error en la búsqueda:', error));
    }

    /**
     * Vincula los links de paginación para que funcionen via AJAX.
     */
    function vincularPaginacion() {
        const linksPaginacion = contenedorTabla.querySelectorAll('.paginacion-botones a');

        linksPaginacion.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                buscarProductos(this.href);
            });
        });
    }

    // Escuchar el input de búsqueda con debounce
    inputBusqueda.addEventListener('input', function () {
        clearTimeout(timeoutBusqueda);
        timeoutBusqueda = setTimeout(() => {
            buscarProductos();
        }, 300);
    });

    // =============================================
    //  CONFIRMAR OPERACIÓN (preparar datos)
    // =============================================

    const botonConfirmar = document.querySelector('.boton-confirmar-operacion');

    botonConfirmar.addEventListener('click', function () {
        const filas = cuerpoCarrito.querySelectorAll('tr');

        // Validar que haya al menos un producto en el carrito
        if (filas.length === 0) {
            alert('Agregá al menos un producto antes de confirmar.');
            return;
        }

        // Recopilar los items del carrito
        const items = [];
        filas.forEach(fila => {
            items.push({
                id_producto: fila.dataset.id,
                cantidad: parseInt(fila.querySelector('.input-cantidad').value)
            });
        });

        // Obtener el método de pago seleccionado
        const metodoPago = document.querySelector('input[name="metodo_pago"]:checked').value;

        // Armar el objeto con todos los datos de la operación
        const datosOperacion = {
            items: items,
            metodo_pago: metodoPago
        };

        console.log('Datos listos para enviar al servidor:', datosOperacion);

        // TODO: Enviar datosOperacion al servidor via fetch/POST
        // Una vez confirmado exitosamente, limpiar el carrito:
        // limpiarCarritoStorage();
    });

    // Guardar el carrito antes de que la página se cierre o recargue
    window.addEventListener('beforeunload', function () {
        const filas = cuerpoCarrito.querySelectorAll('tr');
        if (filas.length > 0) {
            guardarCarrito();
        }
    });

    // =============================================
    //  INICIALIZACIÓN
    // =============================================

    restaurarCarrito();
    vincularBotonesAgregar();
    vincularPaginacion();
});
