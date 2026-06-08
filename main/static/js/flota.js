// =============================================
//  GESTIÓN DE CHOFERES Y VEHÍCULOS (FLOTA)
//  Reusa los slide-overs (paneles.js) para alta y edición,
//  cambiando la accion/titulo/campos segun el caso.
// =============================================

// ---------- CHOFER ----------

function abrirNuevoChofer() {
    document.getElementById('accion-chofer').value = 'nuevo_chofer';
    document.getElementById('id-chofer-input').value = '';
    document.getElementById('nombre-chofer').value = '';
    document.getElementById('apellido-chofer').value = '';
    document.getElementById('titulo-chofer').textContent = 'Nuevo Chofer';
    abrirSlideOver('slide-over-chofer');
}

function abrirEditarChofer(boton) {
    document.getElementById('accion-chofer').value = 'editar_chofer';
    document.getElementById('id-chofer-input').value = boton.dataset.id;
    document.getElementById('nombre-chofer').value = boton.dataset.nombre;
    document.getElementById('apellido-chofer').value = boton.dataset.apellido;
    document.getElementById('titulo-chofer').textContent = 'Editar Chofer';
    abrirSlideOver('slide-over-chofer');
}

// ---------- VEHÍCULO ----------

function abrirNuevoVehiculo() {
    document.getElementById('accion-vehiculo').value = 'nuevo_vehiculo';
    document.getElementById('id-vehiculo-input').value = '';
    document.getElementById('nombre-vehiculo').value = '';
    document.getElementById('patente-vehiculo').value = '';
    document.getElementById('titulo-vehiculo').textContent = 'Nuevo Vehículo';
    abrirSlideOver('slide-over-vehiculo');
}

function abrirEditarVehiculo(boton) {
    document.getElementById('accion-vehiculo').value = 'editar_vehiculo';
    document.getElementById('id-vehiculo-input').value = boton.dataset.id;
    document.getElementById('nombre-vehiculo').value = boton.dataset.nombre;
    document.getElementById('patente-vehiculo').value = boton.dataset.patente;
    document.getElementById('titulo-vehiculo').textContent = 'Editar Vehículo';
    abrirSlideOver('slide-over-vehiculo');
}

// ---------- ELIMINAR (modal de confirmación) ----------

function abrirEliminarFlota(tipo, boton) {
    const id = boton.dataset.id;
    const nombre = boton.dataset.nombre;

    const inputChofer = document.getElementById('id-eliminar-chofer');
    const inputVehiculo = document.getElementById('id-eliminar-vehiculo');

    // Dejo habilitado solo el campo del tipo correspondiente (los disabled no se envian)
    if (tipo === 'chofer') {
        document.getElementById('accion-eliminar-flota').value = 'eliminar_chofer';
        inputChofer.disabled = false;
        inputChofer.value = id;
        inputVehiculo.disabled = true;
        inputVehiculo.value = '';
    } else {
        document.getElementById('accion-eliminar-flota').value = 'eliminar_vehiculo';
        inputVehiculo.disabled = false;
        inputVehiculo.value = id;
        inputChofer.disabled = true;
        inputChofer.value = '';
    }

    const etiqueta = tipo === 'chofer' ? 'al chofer' : 'el vehículo';
    document.getElementById('texto-eliminar-flota').innerHTML =
        `¿Seguro que quiere eliminar ${etiqueta} <b>${nombre}</b>? Dejará de estar disponible para nuevos viajes.`;

    document.getElementById('modal-eliminar-flota').classList.add('abierto');
    document.body.style.overflow = 'hidden';
}

function cerrarModalEliminarFlota() {
    document.getElementById('modal-eliminar-flota').classList.remove('abierto');
    document.body.style.overflow = 'auto';
}
