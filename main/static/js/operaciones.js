document.addEventListener('DOMContentLoaded', () => {
    const botonesAgregar = document.querySelectorAll('.boton-agregar-producto');
    const cuerpoCarrito = document.getElementById('cuerpo-carrito');
    const elementoTotal = document.querySelector('.total-destacado');
    const inputBusqueda = document.querySelector('.input-busqueda');

    // Claves en sessionStorage para persistir el carrito entre paginación/búsqueda
    const STORAGE_KEY = 'carrito_operacion';
    // Flag que indica si la navegación es interna (paginación/búsqueda dentro de operaciones)
    const NAV_FLAG_KEY = 'carrito_nav_interna';

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
        const esNavInterna = sessionStorage.getItem(NAV_FLAG_KEY);
        // Siempre consumimos la flag después de leerla
        sessionStorage.removeItem(NAV_FLAG_KEY);

        if (!esNavInterna) {
            // No venimos de paginación/búsqueda interna → limpiar cualquier carrito viejo
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

    /** Limpia el carrito y la flag del storage */
    function limpiarCarritoStorage() {
        sessionStorage.removeItem(STORAGE_KEY);
        sessionStorage.removeItem(NAV_FLAG_KEY);
    }

    /** Marca que la próxima navegación es interna (paginación/búsqueda) */
    function marcarNavegacionInterna() {
        sessionStorage.setItem(NAV_FLAG_KEY, 'true');
    }

    // =============================================
    //  CONTROL DE STOCK VISUAL
    // =============================================

    /**
     * Busca la fila del producto en la tabla de listado por su ID.
     * Retorna { fila, stockCell, boton } o null si el producto no está en la página actual.
     */
    function buscarProductoEnTabla(idProducto) {
        const boton = document.querySelector(`.boton-agregar-producto[data-id="${idProducto}"]`);
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
        if (!producto) return; // El producto no está en la página actual

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
     * que estén visibles en la tabla de listado. Se usa al restaurar el carrito.
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

    /**
     * Obtiene el stock original de un producto.
     * Primero busca en la tabla visible, si no está, busca en el carrito.
     */
    function obtenerStockOriginal(idProducto) {
        // Buscar en la tabla de productos visible
        const producto = buscarProductoEnTabla(idProducto);
        if (producto) {
            return parseInt(producto.boton.dataset.stock);
        }

        // Si no está visible, buscar en el carrito (ya fue agregado antes)
        const filaCarrito = cuerpoCarrito.querySelector(`tr[data-id="${idProducto}"]`);
        if (filaCarrito) {
            return parseInt(filaCarrito.dataset.stockOriginal);
        }

        return 0;
    }

    // =============================================
    //  LÓGICA DEL CARRITO
    // =============================================

    // Manejar el evento de agregar producto al carrito
    botonesAgregar.forEach(boton => {
        boton.addEventListener('click', function () {
            const id = this.dataset.id;
            const nombre = this.dataset.nombre;
            const precioStr = this.dataset.precio;
            const precio = parseFloat(precioStr.replace(',', '.'));
            const stockOriginal = parseInt(this.dataset.stock);

            agregarAlCarrito(id, nombre, precio, stockOriginal);
        });
    });

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
            // Actualizar el stock visual: restar 1
            actualizarStockProducto(id, stockOriginal - (cantidadActual + 1));
        } else {
            // Validar que haya stock
            if (stockOriginal <= 0) {
                return;
            }

            crearFilaCarrito(id, nombre, precio, 1, stockOriginal);
            // Actualizar el stock visual: restar 1
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
        let cantidadAnterior = cantidad;

        inputCantidad.addEventListener('input', function () {
            let val = parseInt(this.value);

            if (isNaN(val) || val < 1) {
                val = 1;
                this.value = 1;
            }

            // No permitir superar el stock original
            if (val > stockOriginal) {
                val = stockOriginal;
                this.value = stockOriginal;
            }

            // Actualizar el stock visual con la diferencia
            const stockDisponible = stockOriginal - val;
            actualizarStockProducto(id, stockDisponible);

            cantidadAnterior = val;
            actualizarTotal();
            guardarCarrito();
        });

        // Lógica para eliminar la fila: restaurar stock y actualizar
        const botonEliminar = fila.querySelector('.boton-eliminar-item');
        botonEliminar.addEventListener('click', function () {
            const cantidadEliminada = parseInt(inputCantidad.value);
            fila.remove();

            // Restaurar el stock visual del producto
            actualizarStockProducto(id, stockOriginal);

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
    //  BUSCADOR DE PRODUCTOS
    // =============================================

    let timeoutBusqueda = null;

    inputBusqueda.addEventListener('input', function () {
        clearTimeout(timeoutBusqueda);
        const query = this.value.trim();

        // Debounce de 500ms para no recargar en cada tecla
        timeoutBusqueda = setTimeout(() => {
            const url = new URL(window.location.href);

            if (query) {
                url.searchParams.set('q', query);
            } else {
                url.searchParams.delete('q');
            }
            // Resetear a la página 1 cuando se busca
            url.searchParams.delete('page');

            // Marcar como navegación interna para preservar el carrito
            marcarNavegacionInterna();
            window.location.href = url.toString();
        }, 500);
    });

    // Restaurar el texto de búsqueda en el input al cargar la página
    const urlParams = new URLSearchParams(window.location.search);
    const queryActual = urlParams.get('q');
    if (queryActual) {
        inputBusqueda.value = queryActual;
    }

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

    // =============================================
    //  NAVEGACIÓN INTERNA (preservar carrito)
    // =============================================

    // Los links de paginación (href="?page=...") son navegación interna
    document.addEventListener('click', function (e) {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        if (href && href.startsWith('?')) {
            // Es un link de paginación → marcar para preservar el carrito
            marcarNavegacionInterna();
        }
    });

    // =============================================
    //  INICIALIZACIÓN
    // =============================================

    restaurarCarrito();
});
