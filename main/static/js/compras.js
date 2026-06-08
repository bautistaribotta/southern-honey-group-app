document.addEventListener('DOMContentLoaded', () => {
    const cuerpoCarrito = document.getElementById('cuerpo-carrito');
    const elementoTotal = document.querySelector('.total-destacado');
    const inputBusqueda = document.querySelector('.input-busqueda');
    const contenedorTabla = document.getElementById('contenedor-tabla-compras');

    // Formateador en formato argentino (separador de miles con punto)
    const formatoMoneda = new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // Clave en sessionStorage para persistir el carrito de compra
    const STORAGE_KEY = 'carrito_compra';

    // =============================================
    //  PERSISTENCIA DEL CARRITO (sessionStorage)
    // =============================================

    function guardarCarrito() {
        const filas = cuerpoCarrito.querySelectorAll('tr');
        const items = [];
        filas.forEach(fila => {
            items.push({
                id: fila.dataset.id,
                nombre: fila.querySelector('.item-nombre').textContent,
                cantidad: parseInt(fila.querySelector('.input-cantidad').value),
                precio: fila.querySelector('.input-precio-item').value
            });
        });
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    }

    function restaurarCarrito() {
        // Detectar si la página fue recargada (F5) o es una navegación nueva
        const navegacion = performance.getEntriesByType('navigation')[0];
        const esRecarga = navegacion && navegacion.type === 'reload';

        if (!esRecarga) {
            // Navegación nueva → limpiar cualquier carrito viejo
            sessionStorage.removeItem(STORAGE_KEY);
            return;
        }

        const datos = sessionStorage.getItem(STORAGE_KEY);
        if (!datos) return;

        const items = JSON.parse(datos);
        items.forEach(item => {
            crearFilaCarrito(item.id, item.nombre, item.cantidad, item.precio);
        });
        actualizarTotal();
    }

    /** Limpia el carrito del storage */
    function limpiarCarritoStorage() {
        sessionStorage.removeItem(STORAGE_KEY);
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
                agregarAlCarrito(this.dataset.id, this.dataset.nombre);
            });
        });
    }

    function agregarAlCarrito(id, nombre) {
        const filaExistente = cuerpoCarrito.querySelector(`tr[data-id="${id}"]`);

        if (filaExistente) {
            // En compra no hay tope de stock: sumar 1 sin límite
            const inputCantidad = filaExistente.querySelector('.input-cantidad');
            inputCantidad.value = parseInt(inputCantidad.value) + 1;
        } else {
            // Precio vacío: lo carga el usuario a mano
            crearFilaCarrito(id, nombre, 1, '');
        }

        actualizarTotal();
        guardarCarrito();
    }

    function crearFilaCarrito(id, nombre, cantidad, precio) {
        const fila = document.createElement('tr');
        fila.dataset.id = id;

        fila.innerHTML = `
            <td class="texto-centrado">
                <input type="number" class="input-cantidad" value="${cantidad}" min="1">
            </td>
            <td>
                <div class="item-nombre" title="${nombre}">${nombre}</div>
                <div class="fila-precio-compra">
                    <span class="prefijo-precio">$</span>
                    <input type="number" class="input-precio-item" placeholder="0.00" min="0" step="0.01" value="${precio}">
                    <span class="texto-cu">c/u</span>
                </div>
                <div class="item-subtotal">Subtotal: $ 0.00</div>
            </td>
            <td class="texto-derecha">
                <button type="button" class="boton-eliminar-item"><span class="material-symbols-outlined">delete</span></button>
            </td>
        `;

        const inputCantidad = fila.querySelector('.input-cantidad');
        const inputPrecio = fila.querySelector('.input-precio-item');

        function alCambiar() {
            let cant = parseInt(inputCantidad.value);
            if (isNaN(cant) || cant < 1) {
                cant = 1;
                inputCantidad.value = 1;
            }
            actualizarSubtotalFila(fila);
            actualizarTotal();
            guardarCarrito();
        }

        inputCantidad.addEventListener('input', alCambiar);
        inputPrecio.addEventListener('input', alCambiar);

        const botonEliminar = fila.querySelector('.boton-eliminar-item');
        botonEliminar.addEventListener('click', function () {
            const cantidadActual = parseInt(inputCantidad.value);
            if (cantidadActual > 1) {
                inputCantidad.value = cantidadActual - 1;
                actualizarSubtotalFila(fila);
            } else {
                fila.remove();
            }
            actualizarTotal();
            guardarCarrito();
        });

        cuerpoCarrito.appendChild(fila);
        actualizarSubtotalFila(fila);
    }

    function actualizarSubtotalFila(fila) {
        const cantidad = parseInt(fila.querySelector('.input-cantidad').value) || 0;
        const precio = parseFloat(fila.querySelector('.input-precio-item').value) || 0;
        const subtotal = cantidad * precio;
        fila.querySelector('.item-subtotal').textContent = `Subtotal: $ ${formatoMoneda.format(subtotal)}`;
    }

    function actualizarTotal() {
        let total = 0;
        const filasCarrito = cuerpoCarrito.querySelectorAll('tr');

        filasCarrito.forEach(fila => {
            const cantidad = parseInt(fila.querySelector('.input-cantidad').value) || 0;
            const precio = parseFloat(fila.querySelector('.input-precio-item').value) || 0;
            total += cantidad * precio;
        });

        elementoTotal.textContent = `$ ${formatoMoneda.format(total)}`;
    }

    // =============================================
    //  BUSCADOR DE PRODUCTOS (AJAX)
    // =============================================

    let timeoutBusqueda = null;

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
                vincularBotonesAgregar();
                vincularPaginacion();
            })
            .catch(error => console.error('Error en la búsqueda:', error));
    }

    function vincularPaginacion() {
        const linksPaginacion = contenedorTabla.querySelectorAll('.paginacion-botones a');

        linksPaginacion.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                buscarProductos(this.href);
            });
        });
    }

    inputBusqueda.addEventListener('input', function () {
        clearTimeout(timeoutBusqueda);
        timeoutBusqueda = setTimeout(() => {
            buscarProductos();
        }, 300);
    });

    // =============================================
    //  CONFIRMAR COMPRA (enviar al servidor)
    // =============================================

    const botonConfirmar = document.querySelector('.boton-confirmar-operacion');

    function obtenerCSRFToken() {
        const cookie = document.cookie.split('; ').find(c => c.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    function avisar(mensaje) {
        if (typeof notificarError === 'function') {
            notificarError(mensaje);
        } else {
            alert(mensaje);
        }
    }

    botonConfirmar.addEventListener('click', function () {
        const filas = cuerpoCarrito.querySelectorAll('tr');

        if (filas.length === 0) {
            avisar('Agregá al menos un producto antes de confirmar.');
            return;
        }

        // Recopilar los items del carrito validando precio > 0
        const items = [];
        let precioInvalido = false;

        filas.forEach(fila => {
            const cantidad = parseInt(fila.querySelector('.input-cantidad').value);
            const precioStr = fila.querySelector('.input-precio-item').value.trim();
            const precio = parseFloat(precioStr);

            if (isNaN(precio) || precio <= 0) {
                precioInvalido = true;
            }

            items.push({
                id_producto: fila.dataset.id,
                cantidad: cantidad,
                // Enviar como string para que Django lo convierta a Decimal sin ruido de float
                precio_unitario: precioStr
            });
        });

        if (precioInvalido) {
            avisar('Cargá un precio mayor a 0 en todos los productos.');
            return;
        }

        const metodoPagoSeleccionado = document.querySelector('input[name="metodo_pago"]:checked');

        if (!metodoPagoSeleccionado) {
            avisar('Seleccioná un método de pago antes de continuar.');
            return;
        }

        const metodoPago = metodoPagoSeleccionado.value;

        botonConfirmar.disabled = true;
        botonConfirmar.textContent = 'Procesando...';

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCSRFToken(),
            },
            body: JSON.stringify({
                items: items,
                metodo_pago: metodoPago,
                tipo_operacion: 'compra',
            }),
        })
            .then(response => response.json().then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                if (ok && data.ok) {
                    limpiarCarritoStorage();
                    window.location.href = `/informacion_clientes/${data.id_cliente}/`;
                } else {
                    avisar(data.error || 'Algo salió mal. Por favor, volvé a intentarlo.');
                    botonConfirmar.disabled = false;
                    botonConfirmar.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Confirmar Compra';
                }
            })
            .catch(error => {
                console.error('Error en la petición:', error);
                avisar('Algo salió mal. Por favor, volvé a intentarlo.');
                botonConfirmar.disabled = false;
                botonConfirmar.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Confirmar Compra';
            });
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
