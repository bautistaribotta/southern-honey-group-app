import re
from datetime import datetime
import requests
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache
from .models import Producto, Cliente, Operacion, DetalleOperacion, Pago, Cotizaciones, Chofer, Vehiculo, Viaje, DetalleViaje


# --- Validadores REGEX ---
REGEX_TEXTO_BASICO = re.compile(r"^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]+$")
REGEX_TEXTO_NUMEROS = re.compile(r"^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s\d]+$")
REGEX_PATENTE = re.compile(r"^[A-Z0-9]{6,7}$")


def nuevo_producto(nombre, categoria=None, precio=None, cantidad=None):
    nuevo_producto = Producto.objects.create(
        nombre=nombre, categoria=categoria, precio=precio, cantidad=cantidad
    )
    return nuevo_producto


def obtener_datos_producto(id_producto):
    try:
        # Busco el producto asegurándome de que esté activo en el inventario
        producto = Producto.objects.get(id=id_producto, activo=True)

        # Estructuro la información en un diccionario limpio para que la API JSON lo consuma fácilmente
        return {
            "id": producto.id,
            "nombre": producto.nombre,
            "categoria": producto.categoria,
            "precio": str(
                producto.precio
            ),  # Convierto el Decimal a string para evitar errores de serialización JSON
            "cantidad": str(producto.cantidad),
        }
    except Producto.DoesNotExist:
        # Si el producto no existe o está inactivo, devuelvo None
        return None


def modificar_stock(id_producto, cantidad):
    """
    Modifica el stock de un producto sumando o restando según el valor de 'cantidad'.
    - cantidad > 0 → suma stock (ingreso de mercadería, devolución, etc.)
    - cantidad < 0 → resta stock (venta, egreso, etc.)

    Retorna el producto actualizado o lanza ValueError si el stock quedaría negativo.
    """
    producto = get_object_or_404(Producto, id=id_producto, activo=True)

    # Si estoy restando, válido que haya stock suficiente antes de operar
    if cantidad < 0 and producto.cantidad < abs(cantidad):
        raise ValueError("No se puede quitar más stock del existente.")

    producto.cantidad += cantidad
    producto.save()
    return producto


def editar_producto(id_producto, nombre, categoria, precio, cantidad, activo):
    producto = get_object_or_404(Producto, id=id_producto)

    producto.nombre = nombre
    producto.categoria = categoria
    producto.precio = precio
    producto.cantidad = cantidad
    producto.activo = activo

    producto.save()
    return producto


def eliminar_producto(id_producto):
    producto = get_object_or_404(Producto, id=id_producto)

    # En lugar de borrarlo de la base de datos, lo marco como inactivo
    # para no perder el historial de ventas en las otras tablas
    producto.activo = False
    producto.save()
    return producto


def nuevo_cliente(nombre, apellido=None, telefono=None, localidad=None, direccion=None, factura_produccion=False, cuit=None):
    nuevo_cliente = Cliente.objects.create(
        nombre=nombre,
        apellido=apellido,
        telefono=telefono,
        localidad=localidad,
        direccion=direccion,
        factura_produccion=factura_produccion,
        cuit=cuit,
    )
    return nuevo_cliente


def obtener_datos_cliente(id_cliente):
    try:
        # Busco al cliente asegurándome de que esté activo para no exponer datos de registros "eliminados"
        cliente = Cliente.objects.get(id=id_cliente, activo=True)

        # Estructuro la información en un diccionario para que sea fácil de consumir,
        # ya sea para una respuesta JSON o para cualquier otra lógica interna del sistema
        return {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "apellido": cliente.apellido,
            "telefono": cliente.telefono,
            "localidad": cliente.localidad,
            "direccion": cliente.direccion,
            "factura": cliente.factura_produccion,
            "cuit": cliente.cuit,
        }
    except Cliente.DoesNotExist:
        return None


def editar_cliente(id_cliente, nombre, apellido, telefono, localidad, direccion, factura_produccion, cuit, activo):
    cliente = get_object_or_404(Cliente, id=id_cliente)

    cliente.nombre = nombre
    cliente.apellido = apellido
    cliente.telefono = telefono
    cliente.localidad = localidad
    cliente.direccion = direccion
    cliente.factura_produccion = factura_produccion
    cliente.cuit = cuit
    cliente.activo = activo

    cliente.save()
    return cliente


def eliminar_cliente(id_cliente):
    cliente = get_object_or_404(Cliente, id=id_cliente)
    cliente.activo = False

    cliente.save()
    return cliente


def crear_operacion(cliente, items, metodo_pago):
    # Obtenemos las cotizaciones actuales antes de la transacción
    cotizacion_dolar = get_cotizacion_dolar_oficial()
    if cotizacion_dolar:
        valor_dolar = cotizacion_dolar.get("venta")
    else:
        valor_dolar = None

    valor_miel = get_cotizacion_miel_50mm()

    with transaction.atomic():
        # Creo la operación con las cotizaciones actuales
        operacion = Operacion.objects.create(
            cliente=cliente,
            valor_dolar=valor_dolar,
            valor_kilo_miel=valor_miel
        )

        monto_total = 0

        for item in items:
            id_producto = item.get("id_producto")
            cantidad = int(item.get("cantidad", 0))

            producto = get_object_or_404(Producto, id=id_producto, activo=True)

            # Resto el stock y sumo a la cantidad vendida
            modificar_stock(id_producto, -cantidad)
            producto.refresh_from_db()
            producto.cantidad_vendida += cantidad
            producto.save()

            # Creo el detalle vinculado a la operación
            DetalleOperacion.objects.create(
                operacion=operacion,
                producto=producto,
                cantidad=cantidad,
            )

            monto_total += producto.precio * cantidad

        # Actualizo el monto total de la operación
        operacion.monto_total = monto_total
        operacion.save()

        # Si el pago es "contado", generamos automáticamente un pago
        if metodo_pago.lower() == "contado":
            Pago.objects.create(
                operacion=operacion,
                monto=monto_total
            )

    return operacion


def servicio_cancelar_operacion(id_operacion):
    with transaction.atomic():
        operacion = get_object_or_404(Operacion, id=id_operacion)

        # Si ya está cancelada, no hacemos nada
        if not operacion.activa:
            return operacion

        detalles = DetalleOperacion.objects.filter(operacion=operacion)

        # Restauramos el stock de cada producto en el detalle
        for detalle in detalles:
            producto = detalle.producto
            modificar_stock(producto.id, detalle.cantidad)

            # Restamos de la cantidad vendida históricamente
            producto.refresh_from_db()
            producto.cantidad_vendida -= detalle.cantidad
            producto.save()

        # Marcamos la operación como inactiva (cancelada)
        operacion.activa = False
        operacion.save()

    return operacion


def obtener_listado_deudores(q=""):
    dolar_actual_data = get_cotizacion_dolar_oficial()
    dolar_actual = Decimal(str(dolar_actual_data.get("venta") or 1))  # Prevención división por 0 si falla la API
    
    miel_actual_data = get_cotizacion_miel_50mm()
    try:
        miel_actual = Decimal(str(miel_actual_data)) if miel_actual_data else None
    except ValueError:
        miel_actual = None

    # Filtramos operaciones activas donde el total pagado es menor al monto total
    from django.db.models import DecimalField
    operaciones_adeudadas = (
        Operacion.objects.filter(activa=True)
        .annotate(pagado=Coalesce(Sum('pago__monto'), Value(0), output_field=DecimalField()))
        .filter(monto_total__gt=F('pagado'))
        .select_related('cliente')
        .order_by('-fecha')
    )

    if q:
        from django.db.models import Q
        if q.isdigit():
            operaciones_adeudadas = operaciones_adeudadas.filter(id__icontains=q)
        else:
            operaciones_adeudadas = operaciones_adeudadas.filter(
                Q(cliente__nombre__icontains=q) | Q(cliente__apellido__icontains=q)
            )

    lista_deudores = []
    for operacion in operaciones_adeudadas:
        # La deuda es igual al monto total - los pagos registrados en esa operacion
        deuda_pesos = operacion.monto_total - operacion.pagado
        
        # Cálculos del dólar
        valor_dolar_historico = operacion.valor_dolar if operacion.valor_dolar else None
        
        # Usamos división porque el total está en pesos (Pesos / Valor Dólar = Dólares)
        deuda_dolar_historico = (deuda_pesos / valor_dolar_historico) if valor_dolar_historico else None
        deuda_dolar_actual = (deuda_pesos / dolar_actual) if dolar_actual else None

        # Cálculos de la Miel
        valor_miel_historico = operacion.valor_kilo_miel if operacion.valor_kilo_miel else None
        
        kg_miel_historico = (deuda_pesos / valor_miel_historico) if valor_miel_historico else None
        kg_miel_actual = (deuda_pesos / miel_actual) if miel_actual else None

        lista_deudores.append({
            "id": operacion.id,
            "cliente": f"{operacion.cliente.nombre} {operacion.cliente.apellido or ''}".strip(),
            "fecha": operacion.fecha,
            "deuda_pesos": deuda_pesos,
            "deuda_dolar_historico": round(deuda_dolar_historico, 2) if deuda_dolar_historico else None,
            "deuda_dolar_actual": round(deuda_dolar_actual, 2) if deuda_dolar_actual else None,
            "kg_miel_historico": round(kg_miel_historico, 2) if kg_miel_historico else None,
            "kg_miel_actual": round(kg_miel_actual, 2) if kg_miel_actual else None
        })

    return lista_deudores


def get_cotizacion_dolar_oficial():
    cotizacion = cache.get("cotizacion_oficial")
    if cotizacion:
        return cotizacion

    url_dolar_oficial = "https://dolarapi.com/v1/dolares/oficial"
    try:
        respuesta = requests.get(url_dolar_oficial, verify=True)
        datos = respuesta.json()
        resultado = {"compra": datos.get("compra"), "venta": datos.get("venta")}
        cache.set("cotizacion_oficial", resultado, 3600)  # Cache por 1 hora
        return resultado
    except Exception as e:
        return {"compra": None, "venta": None}


def get_cotizaciones():
    """
    Obtiene todas las cotizaciones guardadas en la base de datos.
    Retorna un diccionario con el formato {articulo_sanitizado: monto}
    donde los caracteres especiales se reemplazan para facilitar su uso en templates.
    """
    articulos_esperados = ["Miel 34mm", "Miel 50mm", "Miel +50mm", "Cera Operculo", "Cera Recupero"]
    cotizaciones_db = {c.articulo: c.monto for c in Cotizaciones.objects.all()}
    
    resultado = {}
    for art in articulos_esperados:
        # Sanitizar la clave para que sea un identificador válido en Django Templates
        clave = art.replace(" ", "_").replace("+", "plus")
        resultado[clave] = cotizaciones_db.get(art, 0)
        
    return resultado


def actualizar_cotizacion(articulo, monto):
    """
    Actualiza o crea una cotización en la base de datos.
    """
    cotizacion, created = Cotizaciones.objects.update_or_create(
        articulo=articulo,
        defaults={"monto": monto}
    )
    return cotizacion


def get_cotizacion_miel_50mm():
    """
    Obtiene la cotización de la miel. Se toma 'Miel 50mm' como referencia por defecto.
    """
    try:
        miel = Cotizaciones.objects.get(articulo="Miel 50mm")
        return miel.monto
    except Cotizaciones.DoesNotExist:
        return 1.00


def crear_chofer(nombre, apellido):
    # Aplico limpieza de espacios
    nombre = nombre.strip()
    apellido = apellido.strip()

    # Valido la longitud y formato del nombre
    if not (3 <= len(nombre) <= 25) or not REGEX_TEXTO_BASICO.match(nombre):
        raise ValueError("El nombre debe tener entre 3 y 25 letras, sin números ni símbolos.")

    # Valido la longitud y formato del apellido
    if not (3 <= len(apellido) <= 25) or not REGEX_TEXTO_BASICO.match(apellido):
        raise ValueError("El apellido debe tener entre 3 y 25 letras, sin números ni símbolos.")

    nuevo_chofer = Chofer.objects.create(
        nombre=nombre,
        apellido=apellido
    )
    return nuevo_chofer


def editar_chofer(id_chofer, nombre, apellido, activo):
    chofer = get_object_or_404(Chofer, id=id_chofer)
    chofer.nombre = nombre
    chofer.apellido = apellido
    chofer.activo = activo

    chofer.save()
    return chofer


def eliminar_chofer(id_chofer):
    chofer = get_object_or_404(Chofer, id=id_chofer)
    chofer.activo = False
    chofer.save()
    return chofer


def crear_vehiculo(nombre, patente):
    # Aplico limpieza de espacios y fuerzo la patente a mayúsculas
    nombre = nombre.strip()
    patente = patente.strip().upper()

    # Valido la longitud y formato del nombre del vehículo
    if not (3 <= len(nombre) <= 25) or not REGEX_TEXTO_NUMEROS.match(nombre):
        raise ValueError("El nombre del vehículo debe tener entre 3 y 25 caracteres (solo letras y números).")

    # Valido la longitud y formato de la patente
    if not patente or not REGEX_PATENTE.match(patente):
        raise ValueError("La patente debe tener 6 o 7 caracteres alfanuméricos sin espacios.")

    nuevo_vehiculo = Vehiculo.objects.create(
        nombre=nombre,
        patente=patente
    )
    return nuevo_vehiculo


def editar_vehiculo(id_vehiculo, nombre, patente, activo):
    vehiculo = get_object_or_404(Vehiculo, id=id_vehiculo)
    vehiculo.nombre = nombre
    vehiculo.patente = patente
    vehiculo.activo = activo

    vehiculo.save()
    return vehiculo


def eliminar_vehiculo(id_vehiculo):
    vehiculo = get_object_or_404(Vehiculo, id=id_vehiculo)
    vehiculo.activo = False
    vehiculo.save()
    return vehiculo


def crear_viaje(id_chofer, id_vehiculo, destinos, inicio_caja, fecha_inicio, fecha_vuelta=None):
    """
    Crea un viaje (maestro) y sus destinos asociados (detalle) usando una transacción atómica.
    'destinos' debe ser una lista de strings. Ejemplo: ["Buenos Aires", "Rosario"].
    """
    # 1. Valido que el chofer exista en la base de datos
    if not Chofer.objects.filter(id=id_chofer).exists():
        raise ValueError("El chofer seleccionado no existe en el sistema.")

    # 2. Valido que el vehículo exista en la base de datos
    if not Vehiculo.objects.filter(id=id_vehiculo).exists():
        raise ValueError("El vehículo seleccionado no existe en el sistema.")

    # 3. Valido los destinos
    if not destinos:
        raise ValueError("Debe ingresar al menos un destino.")

    destinos_limpios = []
    for d in destinos:
        d_limpio = d.strip()
        if not (3 <= len(d_limpio) <= 30) or not REGEX_TEXTO_NUMEROS.match(d_limpio):
            raise ValueError(f"El destino '{d}' es inválido (debe tener entre 3 y 30 caracteres alfanuméricos).")
        destinos_limpios.append(d_limpio)

    # 4. Valido el inicio de caja
    try:
        caja_val = float(inicio_caja)
        if caja_val < 0 or caja_val > 99999999.99:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("El monto de inicio de caja debe ser un número positivo y no superar el límite permitido de la BD.")

    # 5. Valido estrictamente el formato de las fechas para la BD
    try:
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        if fecha_vuelta: # La fecha de vuelta es opcional
            datetime.strptime(fecha_vuelta, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError("Las fechas deben tener el formato válido YYYY-MM-DD.")

    with transaction.atomic():
        # Creamos el viaje (Tabla Maestra)
        nuevo_viaje = Viaje.objects.create(
            chofer_id=id_chofer,
            vehiculo_id=id_vehiculo,
            inicio_caja=inicio_caja,
            fecha_inicio=fecha_inicio,
            fecha_vuelta=fecha_vuelta,
            gastos=0
        )

        # Iteramos sobre la lista de destinos limpios para crear el Detalle
        for destino_nombre in destinos_limpios:
            DetalleViaje.objects.create(
                viaje=nuevo_viaje,
                destino=destino_nombre
            )
            
        # Incremento el contador de viajes del Chofer sumando la cantidad de destinos
        chofer = Chofer.objects.get(id=id_chofer)
        chofer.total_viajes += len(destinos_limpios)
        chofer.save()

        # Incremento el contador de viajes del Vehículo sumando la cantidad de destinos
        vehiculo = Vehiculo.objects.get(id=id_vehiculo)
        vehiculo.total_viajes += len(destinos_limpios)
        vehiculo.save()

    return nuevo_viaje


def obtener_choferes_activos():
    return Chofer.objects.filter(activo=True).order_by('nombre')


def obtener_vehiculos_activos():
    return Vehiculo.objects.filter(activo=True).order_by('nombre')


def obtener_viajes():
    return Viaje.objects.filter(activo=True).select_related('chofer', 'vehiculo').prefetch_related('destinos').order_by('-fecha_inicio')


def editar_viaje(id_viaje, id_chofer, id_vehiculo, destinos, inicio_caja, fecha_inicio, fecha_vuelta):
    # 1. Valido que el chofer exista en la base de datos
    if not Chofer.objects.filter(id=id_chofer).exists():
        raise ValueError("El chofer seleccionado no existe en el sistema.")

    # 2. Valido que el vehículo exista en la base de datos
    if not Vehiculo.objects.filter(id=id_vehiculo).exists():
        raise ValueError("El vehículo seleccionado no existe en el sistema.")

    # 3. Valido los destinos
    if not destinos:
        raise ValueError("Debe ingresar al menos un destino.")

    destinos_limpios = []
    for d in destinos:
        d_limpio = d.strip()
        if not (3 <= len(d_limpio) <= 30) or not REGEX_TEXTO_NUMEROS.match(d_limpio):
            raise ValueError(f"El destino '{d}' es inválido (debe tener entre 3 y 30 caracteres alfanuméricos).")
        destinos_limpios.append(d_limpio)

    # 4. Valido el inicio de caja
    try:
        caja_val = float(inicio_caja)
        if caja_val < 0 or caja_val > 99999999.99:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError("El monto de inicio de caja debe ser un número positivo y no superar el límite permitido de la BD.")

    # 5. Valido estrictamente el formato de las fechas para la BD
    try:
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        if fecha_vuelta: # La fecha de vuelta es opcional
            datetime.strptime(fecha_vuelta, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise ValueError("Las fechas deben tener el formato válido YYYY-MM-DD.")

    with transaction.atomic():
        viaje = get_object_or_404(Viaje, id=id_viaje)
        
        chofer_anterior_id = viaje.chofer_id
        vehiculo_anterior_id = viaje.vehiculo_id
        cantidad_destinos_anterior = viaje.destinos.count()
        
        viaje.chofer_id = id_chofer
        viaje.vehiculo_id = id_vehiculo
        viaje.inicio_caja = inicio_caja
        viaje.fecha_inicio = fecha_inicio
        viaje.fecha_vuelta = fecha_vuelta if fecha_vuelta else None
        viaje.save()
        
        # Eliminar destinos anteriores y crear nuevos
        viaje.destinos.all().delete()
        for destino_nombre in destinos_limpios:
            DetalleViaje.objects.create(
                viaje=viaje,
                destino=destino_nombre
            )
            
        # Actualizar contador de chofer
        if chofer_anterior_id == int(id_chofer):
            chofer = Chofer.objects.get(id=id_chofer)
            chofer.total_viajes = chofer.total_viajes - cantidad_destinos_anterior + len(destinos_limpios)
            chofer.save()
        else:
            chofer_anterior = Chofer.objects.get(id=chofer_anterior_id)
            if chofer_anterior.total_viajes >= cantidad_destinos_anterior:
                chofer_anterior.total_viajes -= cantidad_destinos_anterior
                chofer_anterior.save()
            chofer_nuevo = Chofer.objects.get(id=id_chofer)
            chofer_nuevo.total_viajes += len(destinos_limpios)
            chofer_nuevo.save()
            
        # Actualizar contador de vehiculo
        if vehiculo_anterior_id == int(id_vehiculo):
            vehiculo = Vehiculo.objects.get(id=id_vehiculo)
            vehiculo.total_viajes = vehiculo.total_viajes - cantidad_destinos_anterior + len(destinos_limpios)
            vehiculo.save()
        else:
            vehiculo_anterior = Vehiculo.objects.get(id=vehiculo_anterior_id)
            if vehiculo_anterior.total_viajes >= cantidad_destinos_anterior:
                vehiculo_anterior.total_viajes -= cantidad_destinos_anterior
                vehiculo_anterior.save()
            vehiculo_nuevo = Vehiculo.objects.get(id=id_vehiculo)
            vehiculo_nuevo.total_viajes += len(destinos_limpios)
            vehiculo_nuevo.save()
            
    return viaje


def eliminar_viaje(id_viaje):
    viaje = get_object_or_404(Viaje, id=id_viaje)
    viaje.activo = False
    viaje.save()

    # Decrementar total de viajes de chofer y vehiculo
    # Agrego una capa de redundancia
    chofer = viaje.chofer
    if chofer.total_viajes > 0:
        chofer.total_viajes -= 1
        chofer.save()

    vehiculo = viaje.vehiculo
    if vehiculo.total_viajes > 0:
        vehiculo.total_viajes -= 1
        vehiculo.save()

    return viaje