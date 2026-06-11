document.addEventListener('DOMContentLoaded', () => {
    const cuerpoCarrito = document.getElementById('cuerpo-carrito');
    const elementoTotal = document.getElementById('total-destacado');
    const inputBusqueda = document.querySelector('.input-busqueda');
    const contenedorTabla = document.getElementById('contenedor-tabla-compras');
    const carritoVacio = document.getElementById('carrito-vacio');
    const contadorCarrito = document.getElementById('contador-carrito');
    const botonVaciar = document.getElementById('boton-vaciar-carrito');

    // Formateador en formato argentino (separador de miles con punto)
    const formatoMoneda = new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // Clave en sessionStorage para persistir el carrito de compra
    const STORAGE_KEY = 'carrito_compra';

    // =============================================
    //  PERSISTENCIA DEL CARRITO (sessionStorage)
    // =============================================

    function guardarCarrito() {
        const filas = cuerpoCarrito.querySelectorAll('.cart-item');
        const items = [];
        filas.forEach(fila => {
            items.push({
                id: fila.dataset.id,
                nombre: fila.querySelector('.cart-item__name').textContent,
                cantidad: parseInt(fila.querySelector('.input-cantidad').value),
                precio: fila.querySelector('.input-precio-item').value
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
            crearFilaCarrito(item.id, item.nombre, item.cantidad, item.precio);
        });
        actualizarTotal();
        actualizarVistaResumen();
    }

    function limpiarCarritoStorage() {
        sessionStorage.removeItem(STORAGE_KEY);
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
                agregarAlCarrito(this.dataset.id, this.dataset.nombre);
            });
        });
    }

    function agregarAlCarrito(id, nombre) {
        const filaExistente = cuerpoCarrito.querySelector(`.cart-item[data-id="${id}"]`);

        if (filaExistente) {
            const inputCantidad = filaExistente.querySelector('.input-cantidad');
            inputCantidad.value = parseInt(inputCantidad.value) + 1;
            actualizarSubtotalFila(filaExistente);
        } else {
            crearFilaCarrito(id, nombre, 1, '');
        }

        actualizarTotal();
        guardarCarrito();
    }

    function crearFilaCarrito(id, nombre, cantidad, precio) {
        const fila = document.createElement('div');
        fila.className = 'cart-item';
        fila.dataset.id = id;

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
                    <input type="number" class="input-cantidad" value="${cantidad}" min="1">
                    <button type="button" data-step="mas" title="Sumar"><span class="material-symbols-outlined">add</span></button>
                </div>
                <div class="cart-priceedit">
                    <span class="cart-priceedit__cur">$</span>
                    <input type="number" class="input-precio-item" placeholder="0.00" min="0" step="0.01" value="${precio}">
                </div>
            </div>
            <div class="cart-item__sub2">
                <span class="cart-item__sublabel">Subtotal</span>
                <span class="cart-item__subval">$ 0.00</span>
            </div>
        `;

        const inputCantidad = fila.querySelector('.input-cantidad');
        const botonMenos = fila.querySelector('[data-step="menos"]');
        const botonMas = fila.querySelector('[data-step="mas"]');
        const inputPrecio = fila.querySelector('.input-precio-item');

        function alCambiar() {
            let cant = parseInt(inputCantidad.value);
            if (isNaN(cant) || cant < 1) {
                cant = 1;
                inputCantidad.value = 1;
            }
            botonMenos.disabled = cant <= 1;
            actualizarSubtotalFila(fila);
            actualizarTotal();
            guardarCarrito();
        }

        inputCantidad.addEventListener('input', alCambiar);
        inputPrecio.addEventListener('input', alCambiar);

        botonMenos.addEventListener('click', function () {
            const actual = parseInt(inputCantidad.value);
            if (actual > 1) {
                inputCantidad.value = actual - 1;
                alCambiar();
            }
        });

        botonMas.addEventListener('click', function () {
            inputCantidad.value = parseInt(inputCantidad.value) + 1;
            alCambiar();
        });

        const botonEliminar = fila.querySelector('.cart-item__rm');
        botonEliminar.addEventListener('click', function () {
            fila.remove();
            actualizarTotal();
            actualizarVistaResumen();
            guardarCarrito();
            const btnTabla = contenedorTabla.querySelector(`.boton-agregar-producto[data-id="${id}"]`);
            if (btnTabla) btnTabla.classList.remove('is-incart');
        });

        cuerpoCarrito.appendChild(fila);
        alCambiar();
        actualizarVistaResumen();
        
        const btnTabla = contenedorTabla.querySelector(`.boton-agregar-producto[data-id="${id}"]`);
        if(btnTabla) btnTabla.classList.add('is-incart');
    }

    function actualizarSubtotalFila(fila) {
        const cantidad = parseInt(fila.querySelector('.input-cantidad').value) || 0;
        const precio = parseFloat(fila.querySelector('.input-precio-item').value) || 0;
        const subtotal = cantidad * precio;
        fila.querySelector('.cart-item__subval').textContent = `$ ${formatoMoneda.format(subtotal)}`;
    }

    function actualizarTotal() {
        let total = 0;
        const filasCarrito = cuerpoCarrito.querySelectorAll('.cart-item');

        filasCarrito.forEach(fila => {
            const cantidad = parseInt(fila.querySelector('.input-cantidad').value) || 0;
            const precio = parseFloat(fila.querySelector('.input-precio-item').value) || 0;
            total += cantidad * precio;
        });

        elementoTotal.textContent = `$ ${formatoMoneda.format(total)}`;
    }

    botonVaciar.addEventListener('click', function () {
        cuerpoCarrito.innerHTML = '';
        actualizarTotal();
        actualizarVistaResumen();
        guardarCarrito();
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
                
                // Highlight items already in cart
                const idsCarrito = Array.from(cuerpoCarrito.querySelectorAll('.cart-item')).map(f => f.dataset.id);
                idsCarrito.forEach(id => {
                    const btn = contenedorTabla.querySelector(`.boton-agregar-producto[data-id="${id}"]`);
                    if(btn) btn.classList.add('is-incart');
                });
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
        const filas = cuerpoCarrito.querySelectorAll('.cart-item');

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
                tipo_operacion: 'compra',
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
                    avisar(data.error || 'Algo salió mal. Por favor, volvé a intentarlo.');
                    botonConfirmar.disabled = false;
                    botonConfirmar.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Confirmar compra';
                }
            })
            .catch(error => {
                console.error('Error en la petición:', error);
                avisar('Algo salió mal. Por favor, volvé a intentarlo.');
                botonConfirmar.disabled = false;
                botonConfirmar.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Confirmar compra';
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
