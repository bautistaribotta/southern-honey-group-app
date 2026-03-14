import requests
from bs4 import BeautifulSoup


def nuevo_producto(nombre, categoria=None, precio=None, cantidad=None):
    from .models import Producto
    nuevo_producto = Producto.objects.create(
                    nombre=nombre,
                    categoria=categoria,
                    precio=precio,
                    cantidad=cantidad
    )
    return nuevo_producto


def editar_producto(id_producto, nombre, categoria, precio, cantidad, activo):
    from .models import Producto
    producto = Producto.objects.get(id=id_producto)
    
    producto.nombre = nombre
    producto.categoria = categoria
    producto.precio = precio
    producto.cantidad = cantidad
    producto.activo = activo
    
    producto.save()
    return producto


def eliminar_producto(id_producto):
    from .models import Producto
    producto = Producto.objects.get(id=id_producto)
    
    # En lugar de borrarlo de la base de datos, lo marcamos como inactivo
    # para no perder el historial de ventas en las otras tablas
    producto.activo = False
    producto.save()
    return producto


def nuevo_cliente(nombre, apellido=None, telefono=None, localidad=None, direccion=None, cuit=None, factura_produccion=False):
    from .models import Cliente
    nuevo_cliente = Cliente.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    telefono=telefono,
                    localidad=localidad,
                    direccion=direccion,
                    cuit=cuit,
                    factura_produccion=factura_produccion
    )
    return nuevo_cliente


def editar_cliente(id_cliente, nombre, apellido, telefono, localidad, direccion, cuit, factura_produccion, activo):
    from .models import Cliente
    cliente = Cliente.objects.get(id=id_cliente)
    
    cliente.nombre = nombre
    cliente.apellido = apellido
    cliente.telefono = telefono
    cliente.localidad = localidad
    cliente.direccion = direccion
    cliente.cuit = cuit
    cliente.factura_produccion = factura_produccion
    cliente.activo = activo
    
    cliente.save()
    return cliente


def eliminar_cliente(id_cliente):
    from .models import Cliente
    cliente = Cliente.objects.get(id=id_cliente)
    
    # Marcamos el cliente como inactivo en lugar de borrarlo
    # Esto es clave para no perder el historial de sus compras pasadas
    cliente.activo = False
    cliente.save()
    return cliente




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


def get_cotizacion_miel_clara():
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


def get_cotizacion_miel_oscura():
    url = r"https://infomiel.com/"
    try:
        respuesta = requests.get(url)
        html_resp = respuesta.text
        soup = BeautifulSoup(html_resp, "html.parser")

        # Busco la celda que contiene el texto de referencia
        etiqueta_oscura = soup.find("td", string=lambda t: t and "Miel Oscura" in t)
        # El precio está en la siguiente celda (el hermano de la etiqueta encontrada)
        precio_miel_oscura = etiqueta_oscura.find_next_sibling("td").text

        miel_oscura_limpia = "".join(filter(str.isdigit, precio_miel_oscura))
        return miel_oscura_limpia
    except Exception as e:
        print(f"Error al obtener cotización miel oscura: {e}")  # Quitar a futuro
        return None