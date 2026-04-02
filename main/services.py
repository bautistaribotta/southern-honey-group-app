import requests
from bs4 import BeautifulSoup
from .models import Producto, Cliente, Operacion


def buscar_producto(id_producto):
    producto = Producto.objects.get(id=id_producto)
    return producto


def nuevo_producto(nombre, categoria=None, precio=None, cantidad=None):
    nuevo_producto = Producto.objects.create(
                    nombre=nombre,
                    categoria=categoria,
                    precio=precio,
                    cantidad=cantidad
    )
    return nuevo_producto


def editar_producto(id_producto, nombre, categoria, precio, cantidad, activo):
    producto = Producto.objects.get(id=id_producto)
    
    producto.nombre = nombre
    producto.categoria = categoria
    producto.precio = precio
    producto.cantidad = cantidad
    producto.activo = activo
    
    producto.save()
    return producto


def eliminar_producto(id_producto):
    producto = Producto.objects.get(id=id_producto)
    
    # En lugar de borrarlo de la base de datos, lo marco como inactivo
    # para no perder el historial de ventas en las otras tablas
    producto.activo = False
    producto.save()
    return producto




def buscar_cliente(id_cliente):
    cliente = Cliente.objects.get(id=id_cliente)
    return cliente


def nuevo_cliente(nombre, apellido=None, telefono=None, localidad=None, direccion=None, factura_produccion=False, cuit=None):
    nuevo_cliente = Cliente.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    telefono=telefono,
                    localidad=localidad,
                    direccion=direccion,
                    factura_produccion=factura_produccion,
                    cuit=cuit
    )
    return nuevo_cliente


def editar_cliente(id_cliente, nombre, apellido, telefono, localidad, direccion, factura_produccion, cuit, activo):
    cliente = Cliente.objects.get(id=id_cliente)
    
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
    cliente = Cliente.objects.get(id=id_cliente)
    """
    Marco el cliente como inactivo en lugar de borrarlo
    Esto es clave para no perder el historial de sus compras pasadas
    """
    cliente.activo = False
    cliente.save()
    return cliente


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
            "cuit": cliente.cuit
        }
    except Cliente.DoesNotExist:
        return None



def get_cotizacion_oficial():
    url_dolar_oficial = "https://dolarapi.com/v1/dolares/oficial"
    try:
        respuesta = requests.get(url_dolar_oficial, verify=True)
        datos = respuesta.json()
        return {
            "compra": datos.get("compra"),
            "venta": datos.get("venta")
        }
    except Exception as e:
        print(f"Error al obtener cotización oficial: {e}")  # Quitar a futuro
        return {
            "compra": None,
            "venta": None
        }


def get_cotizacion_blue():
    url_dolar_blue = "https://dolarapi.com/v1/dolares/blue"
    try:
        respuesta = requests.get(url_dolar_blue, verify=True)
        datos = respuesta.json()
        return {
            "compra": datos.get("compra"),
            "venta": datos.get("venta")
        }
    except Exception as e:
        print(f"Error al obtener cotización oficial: {e}")  # Quitar a futuro
        return {
            "compra": None,
            "venta": None
        }


def get_cotizacion_miel():
    url = r"https://infomiel.com/"
    try:
        respuesta = requests.get(url)
        html_resp = respuesta.text
        soup = BeautifulSoup(html_resp, "html.parser")

        # Busco la celda que contiene el texto de referencia
        etiqueta_clara = soup.find("td", string=lambda t: t and "Miel Clara" in t)
        # El precio está en la siguiente celda (el hermano de la etiqueta encontrada)
        precio_miel_clara = etiqueta_clara.find_next_sibling("td").text

        miel_clara_limpia = "".join(filter(str.isdigit, precio_miel_clara))
        return miel_clara_limpia
    except Exception as e:
        print(f"Error al obtener cotización miel clara: {e}")  # Quitar a futuro
        return None


def obtener_datos_producto(id_producto):
    try:
        # Busco el producto asegurándome de que esté activo en el inventario
        producto = Producto.objects.get(id=id_producto, activo=True)
        
        # Estructuro la información en un diccionario limpio para que la API JSON lo consuma fácilmente
        return {
            "id": producto.id,
            "nombre": producto.nombre,
            "categoria": producto.categoria,
            "precio": str(producto.precio), # Convierto el Decimal a string para evitar errores de serialización JSON
            "cantidad": str(producto.cantidad)
        }
    except Producto.DoesNotExist:
        # Si el producto no existe o está inactivo, devuelvo None
        return None