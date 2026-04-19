import requests
from bs4 import BeautifulSoup
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache
from .models import Producto, Cliente, Operacion, DetalleOperacion, Pago


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
        raise ValueError(
            f"Stock insuficiente para '{producto.nombre}'. "
            f"Disponible: {producto.cantidad}, solicitado: {abs(cantidad)}"
        )

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
    """
    Marco el cliente como inactivo en lugar de borrarlo
    Esto es para no perder el historial de sus compras pasadas
    """
    cliente.activo = False
    cliente.save()
    return cliente


def crear_operacion(cliente, items, metodo_pago):
    # Obtenemos las cotizaciones actuales antes de la transacción
    cotizacion_dolar = get_cotizacion_oficial()
    if cotizacion_dolar:
        valor_dolar = cotizacion_dolar.get("venta")
    else:
        # TODO
        """
        Si no se puede obtener la cotizacion del dolar se debe
        pedir al usuario que ingrese el valor de forma manual mediante 
        un modal que lo comunique
        """

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
                monto=int(monto_total)  # Se castea a entero porque en el modelo Pago es IntegerField
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
    dolar_actual_data = get_cotizacion_blue()
    dolar_actual = float(dolar_actual_data.get("venta") or 1) # Prevención división por 0 si falla la API
    
    miel_actual_data = get_cotizacion_miel()
    try:
        miel_actual = float(miel_actual_data) if miel_actual_data else None
    except ValueError:
        miel_actual = None

    # Filtramos operaciones activas donde el total pagado es menor al monto total
    operaciones_adeudadas = (
        Operacion.objects.filter(activa=True)
        .annotate(pagado=Coalesce(Sum('pago__monto'), Value(0)))
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
        deuda_pesos = float(operacion.monto_total) - operacion.pagado
        
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
        print(f"Error al obtener cotización oficial: {e}")  # TODO: Quitar a futuro
        return {"compra": None, "venta": None}


def get_cotizacion_blue():
    cotizacion = cache.get("cotizacion_blue")
    if cotizacion:
        return cotizacion

    url_dolar_blue = "https://dolarapi.com/v1/dolares/blue"
    try:
        respuesta = requests.get(url_dolar_blue, verify=True)
        datos = respuesta.json()
        resultado = {"compra": datos.get("compra"), "venta": datos.get("venta")}
        cache.set("cotizacion_blue", resultado, 3600)  # Cache por 1 hora
        return resultado
    except Exception as e:
        print(
            f"Error al obtener cotización del dolar blue: {e}"
        )  # TODO: Quitar a futuro
        return {"compra": None, "venta": None}


def get_cotizacion_miel():
    cotizacion = cache.get("cotizacion_miel")
    if cotizacion:
        return cotizacion

    url = r"https://infomiel.com/"
    try:
        respuesta = requests.get(url)
        html_resp = respuesta.text
        soup = BeautifulSoup(html_resp, "html.parser")

        # Busco la celda que contiene el texto de referencia
        etiqueta_clara = soup.find("td", string=lambda t: t and "Miel Clara" in t)

        if etiqueta_clara:
            # El precio está en la siguiente celda (el hermano de la etiqueta encontrada)
            precio_miel_clara = etiqueta_clara.find_next_sibling("td").text
            
            # Formatos posibles: "$ 1.500,00", "$1500", "1.500"
            # 1. Quitamos espacios y signos $
            miel_limpia = precio_miel_clara.replace("$", "").replace(" ", "")
            # 2. Si tiene coma (decimales en formato latino), reemplazamos los puntos (miles) por nada y la coma por punto
            if "," in miel_limpia:
                miel_limpia = miel_limpia.replace(".", "").replace(",", ".")
            else:
                pass # Python's float can handle basic strings
            
            # Como regla general, limpiamos todo lo que no sea digito o punto
            miel_final = "".join(c for c in miel_limpia if c.isdigit() or c == '.')
            
            resultado = float(miel_final) if miel_final else None
            cache.set("cotizacion_miel", resultado, 3600)  # Cache por 1 hora
            return resultado

        return None
    except Exception as e:
        print(f"Error al obtener cotización miel: {e}")  # TODO: Quitar a futuro
        return None

