document.addEventListener('DOMContentLoaded', () => {
    const cuerpoCarrito = document.getElementById('cuerpo-carrito');
    const elementoTotal = document.getElementById('total-destacado');
    const inputBusqueda = document.querySelector('.input-busqueda');
    const contenedorTabla = document.getElementById('contenedor-tabla-operaciones');
    const carritoVacio = document.getElementById('carrito-vacio');
    const contadorCarrito = document.getElementById('contador-carrito');
    const botonVaciar = document.getElementById('boton-vaciar-carrito');

    // Formateadores en formato argentino (separador de miles con punto)
    const formatoMoneda = new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const formatoCantidad = new Intl.NumberFormat('es-AR');

    // Clave en sessionStorage para persistir el carrito
    const STORAGE_KEY = 'carrito_operacion';

    // =============================================
    //  PERSISTENCIA DEL CARRITO (sessionStorage)
    // =============================================

    function guardarCarrito() {
        const filas = cuerpoCarrito.querySelectorAll('.cart-item');
        const items = [];
        filas.forEach(fila => {
            items.push({
                id: fila.dataset.id,
                precio: fila.dataset.precio,
                nombre: fila.querySelector('.cart-item__name').textContent,
                cantidad: parseInt(fila.querySelector('.input-cantidad').value),
                stockOriginal: parseInt(fila.dataset.stockOriginal)
            });
        });
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    }

    function restaurarCarrito() {
        const navegacion = performance.getEntriesByType('navigation')[0];
        const esRecarga = navegacion && navegacion.type === 'reload';

        if (!esRecarga) {
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
        ajustarStockVisual();
    }

    function limpiarCarritoStorage() {
        sessionStorage.removeItem(STORAGE_KEY);
    }

    // =============================================
    //  CONTROL DE STOCK VISUAL
    // =============================================

    function buscarProductoEnTabla(idProducto) {
        const boton = contenedorTabla.querySelector(`.boton-agregar-producto[data-id="${idProducto}"]`);
        if (!boton) return null;

        const fila = boton.closest('tr');
        const stockCell = fila.querySelector('.cart-stock');
        return { fila, stockCell, boton };
    }

    function actualizarStockProducto(idProducto, stockDisponible) {
        const producto = buscarProductoEnTabla(idProducto);
        if (!producto) return;

        producto.stockCell.textContent = formatoCantidad.format(stockDisponible);

        if (stockDisponible <= 0) {
            producto.boton.disabled = true;
            producto.boton.classList.add('boton-sin-stock');
            producto.boton.title = "Sin stock disponible";
            producto.stockCell.classList.add('cart-stock--zero');
        } else {
            producto.boton.disabled = false;
            producto.boton.classList.remove('boton-sin-stock');
            producto.boton.title = "Añadir a la venta";
            producto.stockCell.classList.remove('cart-stock--zero');
        }
    }

    function ajustarStockVisual() {
        const filasCarrito = cuerpoCarrito.querySelectorAll('.cart-item');
        filasCarrito.forEach(filaCarrito => {
            const idProducto = filaCarrito.dataset.id;
            const cantidadEnCarrito = parseInt(filaCarrito.querySelector('.input-cantidad').value);
            const stockOriginal = parseInt(filaCarrito.dataset.stockOriginal);
            const stockDisponible = stockOriginal - cantidadEnCarrito;

            actualizarStockProducto(idProducto, stockDisponible);
        });
    }

    // =============================================
    //  ESTADO DEL RESUMEN (vacío / contador)
    // =============================================

    function actualizarVistaResumen() {
        const cantidadItems = cuerpoCarrito.querySelectorAll('.cart-item').length;
        const hayItems = cantidadItems > 0;

        carritoVacio.classList.toggle('oculto', hayItems);
        cuerpoCarrito.classList.toggle('oculto', !hayItems);
        botonVaciar.classList.toggle('oculto', !hayItems);
        contadorCarrito.classList.toggle('oculto', !hayItems);
        contadorCarrito.textContent = cantidadItems;
    }

    // =============================================
    //  LÓGICA DEL CARRITO
    // =============================================

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
        const filaExistente = cuerpoCarrito.querySelector(`.cart-item[data-id="${id}"]`);

        if (filaExistente) {
            const inputCantidad = filaExistente.querySelector('.input-cantidad');
            const cantidadActual = parseInt(inputCantidad.value);

            if (cantidadActual >= stockOriginal) return;

            inputCantidad.value = cantidadActual + 1;
            actualizarFila(filaExistente);
        } else {
            if (stockOriginal <= 0) return;
            crearFilaCarrito(id, nombre, precio, 1, stockOriginal);
        }

        actualizarTotal();
        guardarCarrito();
    }

    function crearFilaCarrito(id, nombre, precio, cantidad, stockOriginal) {
        const fila = document.createElement('div');
        fila.className = 'cart-item';
        fila.dataset.id = id;
        fila.dataset.precio = precio;
        fila.dataset.stockOriginal = stockOriginal;

        fila.innerHTML = `
            <div class="cart-item__top">
                <div>
                    <div class="cart-item__name" title="${nombre}">${nombre}</div>
                </div>
                <button type="button" class="cart-item__rm" title="Quitar">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <div class="cart-item__ctrl">
                <div class="cart-stepper">
                    <button type="button" data-step="menos" title="Restar"><span class="material-symbols-outlined">remove</span></button>
                    <input type="number" class="input-cantidad" value="${cantidad}" min="1" max="${stockOriginal}">
                    <button type="button" data-step="mas" title="Sumar"><span class="material-symbols-outlined">add</span></button>
                </div>
                <span class="cart-pricestatic">$ <strong>${formatoMoneda.format(precio)}</strong> c/u</span>
            </div>
            <div class="cart-item__sub2">
                <span class="cart-item__sublabel">Subtotal</span>
                <span class="cart-item__subval">$ ${formatoMoneda.format(precio * cantidad)}</span>
            </div>
        `;

        const inputCantidad = fila.querySelector('.input-cantidad');
        const botonMenos = fila.querySelector('[data-step="menos"]');
        const botonMas = fila.querySelector('[data-step="mas"]');

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

            actualizarFila(fila);
            actualizarTotal();
            guardarCarrito();
        });

        botonMenos.addEventListener('click', function () {
            const actual = parseInt(inputCantidad.value);
            if (actual > 1) {
                inputCantidad.value = actual - 1;
                actualizarFila(fila);
                actualizarTotal();
                guardarCarrito();
            }
        });

        botonMas.addEventListener('click', function () {
            const actual = parseInt(inputCantidad.value);
            if (actual < stockOriginal) {
                inputCantidad.value = actual + 1;
                actualizarFila(fila);
                actualizarTotal();
                guardarCarrito();
            }
        });

        const botonEliminar = fila.querySelector('.cart-item__rm');
        botonEliminar.addEventListener('click', function () {
            fila.remove();
            actualizarStockProducto(id, stockOriginal);
            actualizarTotal();
            actualizarVistaResumen();
            guardarCarrito();
        });

        cuerpoCarrito.appendChild(fila);
        actualizarFila(fila);
        actualizarVistaResumen();
        
        // Marcar en la tabla que está en carrito
        const btnTabla = contenedorTabla.querySelector(`.boton-agregar-producto[data-id="${id}"]`);
        if(btnTabla) btnTabla.classList.add('is-incart');
    }

    function actualizarFila(fila) {
        const precio = parseFloat(fila.dataset.precio);
        const stockOriginal = parseInt(fila.dataset.stockOriginal);
        const cantidad = parseInt(fila.querySelector('.input-cantidad').value);

        fila.querySelector('.cart-item__subval').textContent = `$ ${formatoMoneda.format(precio * cantidad)}`;
        fila.querySelector('[data-step="menos"]').disabled = cantidad <= 1;
        fila.querySelector('[data-step="mas"]').disabled = cantidad >= stockOriginal;

        actualizarStockProducto(fila.dataset.id, stockOriginal - cantidad);
    }

    function actualizarTotal() {
        let total = 0;
        const filasCarrito = cuerpoCarrito.querySelectorAll('.cart-item');

        filasCarrito.forEach(fila => {
            const precio = parseFloat(fila.dataset.precio);
            const cantidad = parseInt(fila.querySelector('.input-cantidad').value);
            total += precio * cantidad;
        });

        elementoTotal.textContent = `$ ${formatoMoneda.format(total)}`;
    }

    botonVaciar.addEventListener('click', function () {
        const filas = cuerpoCarrito.querySelectorAll('.cart-item');
        filas.forEach(fila => actualizarStockProducto(fila.dataset.id, parseInt(fila.dataset.stockOriginal)));
        cuerpoCarrito.innerHTML = '';
        actualizarTotal();
        actualizarVistaResumen();
        guardarCarrito();
        
        // Remover el highlight
        contenedorTabla.querySelectorAll('.boton-agregar-producto').forEach(btn => btn.classList.remove('is-incart'));
    });

    // =============================================
    //  BUSCADOR DE PRODUCTOS (AJAX)
    // =============================================

    let timeoutBusqueda = null;
    const chips = document.querySelectorAll('.cart-chip');
    const chipActivo = document.querySelector('.cart-chip.is-active');
    let categoriaActual = chipActivo ? (chipActivo.dataset.categoria || '') : '';

    function buscarProductos(urlString = null) {
        let url;

        if (urlString) {
            url = new URL(urlString, window.location.origin);
        } else {
            url = new URL(window.location.href);
            url.searchParams.set('q', inputBusqueda.value.trim());
            url.searchParams.delete('page');
            if (categoriaActual) {
                url.searchParams.set('categoria', categoriaActual);
            } else {
                url.searchParams.delete('categoria');
            }
        }

        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                contenedorTabla.innerHTML = html;
                vincularBotonesAgregar();
                vincularPaginacion();
                ajustarStockVisual();
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

    // Filtro por categoría (chips)
    chips.forEach(chip => {
        chip.addEventListener('click', function () {
            chips.forEach(c => c.classList.remove('is-active'));
            this.classList.add('is-active');
            categoriaActual = this.dataset.categoria || '';
            buscarProductos();
        });
    });

    // =============================================
    //  CONFIRMAR OPERACIÓN (enviar al servidor)
    // =============================================

    const botonConfirmar = document.querySelector('.boton-confirmar-operacion');

    function obtenerCSRFToken() {
        const cookie = document.cookie.split('; ').find(c => c.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    botonConfirmar.addEventListener('click', function () {
        const filas = cuerpoCarrito.querySelectorAll('.cart-item');

        if (filas.length === 0) {
            alert('Agregá al menos un producto antes de confirmar.');
            return;
        }

        const items = [];
        filas.forEach(fila => {
            items.push({
                id_producto: fila.dataset.id,
                cantidad: parseInt(fila.querySelector('.input-cantidad').value)
            });
        });

        const metodoPagoSeleccionado = document.querySelector('input[name="metodo_pago"]:checked');

        if (!metodoPagoSeleccionado) {
            alert('Seleccioná un método de pago antes de continuar.');
            return;
        }

        const metodoPago = metodoPagoSeleccionado.value;

        botonConfirmar.disabled = true;
        botonConfirmar.innerHTML = 'Procesando...';

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerCSRFToken(),
            },
            body: JSON.stringify({
                items: items,
                metodo_pago: metodoPago,
                tipo_operacion: 'venta',
            }),
        })
            .then(response => response.json().then(data => ({ ok: response.ok, data })))
            .then(({ ok, data }) => {
                if (ok && data.ok) {
                    limpiarCarritoStorage();
                    if (data.id_viaje) {
                        window.location.href = `/informacion_viaje/${data.id_viaje}/`;
                    } else {
                        window.location.href = `/informacion_clientes/${data.id_cliente}/`;
                    }
                } else {
                    alert(data.error || 'Algo salió mal. Por favor, volvé a intentarlo.');
                    botonConfirmar.disabled = false;
                    botonConfirmar.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Confirmar venta';
                }
            })
            .catch(error => {
                console.error('Error en la petición:', error);
                alert('Algo salió mal. Por favor, volvé a intentarlo.');
                botonConfirmar.disabled = false;
                botonConfirmar.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Confirmar venta';
            });
    });

    window.addEventListener('beforeunload', function () {
        if (cuerpoCarrito.querySelectorAll('.cart-item').length > 0) guardarCarrito();
    });

    restaurarCarrito();
    actualizarVistaResumen();
    vincularBotonesAgregar();
    vincularPaginacion();
});
