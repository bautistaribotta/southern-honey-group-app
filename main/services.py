import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache
from .models import Producto, Cliente, Operacion, DetalleOperacion, Pago, Cotizaciones, Chofer, Vehiculo, Viaje


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
    cotizacion_dolar = get_cotizacion_oficial()
    if cotizacion_dolar:
        valor_dolar = cotizacion_dolar.get("venta")
    else:
        valor_dolar = None

    valor_miel = get_cotizacion_miel()

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
    dolar_actual_data = get_cotizacion_oficial()
    dolar_actual = float(dolar_actual_data.get("venta") or 1) # Prevención división por 0 si falla la API
    
    miel_actual_data = get_cotizacion_miel()
    try:
        miel_actual = float(miel_actual_data) if miel_actual_data else None
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
        deuda_pesos = float(operacion.monto_total) - float(operacion.pagado)
        
        # Cálculos del dólar
        valor_dolar_historico = float(operacion.valor_dolar) if operacion.valor_dolar else None
        
        # Usamos división porque el total está en pesos (Pesos / Valor Dólar = Dólares)
        deuda_dolar_historico = (deuda_pesos / valor_dolar_historico) if valor_dolar_historico else None
        deuda_dolar_actual = (deuda_pesos / dolar_actual) if dolar_actual else None

        # Cálculos de la Miel
        valor_miel_historico = float(operacion.valor_kilo_miel) if operacion.valor_kilo_miel else None
        
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


def get_cotizacion_oficial():
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


def get_cotizacion_miel():
    """
    Obtiene la cotización de la miel. Se toma 'Miel 50mm' como referencia por defecto.
    """
    try:
        miel = Cotizaciones.objects.get(articulo="Miel 50mm")
        return miel.monto
    except Cotizaciones.DoesNotExist:
        return 1.00


