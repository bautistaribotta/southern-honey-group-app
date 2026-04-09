from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Cliente, Producto, Operacion, DetalleOperacion
from .services import (
    nuevo_producto,
    editar_producto,
    eliminar_producto,
    nuevo_cliente,
    editar_cliente,
    get_cotizacion_oficial,
    get_cotizacion_blue,
    obtener_datos_cliente,
    obtener_datos_producto,
    eliminar_cliente,
)


def login(request):
    if request.method == "POST":
        usuario = request.POST.get("user")
        password = request.POST.get("password")

        usuario_valido = authenticate(request, username=usuario, password=password)

        # Si es válido los redirijo, si no, envío el error por mensaje
        if usuario_valido is not None:
            auth_login(request, usuario_valido)
            return redirect("inicio")

        else:
            messages.error(request, "Usuario y/o contraseña incorrectos")
            return redirect("login")

    return render(request, "login.html")


"""
Si un usuario anónimo (sin loguearse) quiere acceder a las paginas internas, 
le bloqueo el acceso y lo envio de vuelta a '/' (pagina configurada del inicio del server) 
para que se loguee. Todo esto implementado usando el wrapped @login_required
"""


@login_required
def inicio(request):
    dolar_oficial = get_cotizacion_oficial()
    dolar_blue = get_cotizacion_blue()
    contexto = {"oficial": dolar_oficial, "blue": dolar_blue}
    return render(request, "inicio.html", contexto)


@login_required
def productos(request):
    """
    Recibo el metodo POST, guardo los datos del formulario y creo
    el producto en la base de datos, queda realizar validaciones
    """
    if request.method == "POST":
        id_producto = request.POST.get("id_producto")
        nombre_producto = request.POST.get("nombre")
        categoria = request.POST.get("categoria")
        precio = request.POST.get("precio")
        cantidad = request.POST.get("stock")

        # Si el usuario no ingresó un stock (campo vacío), lo coloco en 0
        if not cantidad:
            cantidad = 0

        # Si es una ELIMINACION, aqui traigo el id a borrar
        id_eliminar = request.POST.get("id_eliminar")
        if id_eliminar:
            eliminar_producto(id_eliminar)
            messages.success(request, "Producto eliminado correctamente")
            return redirect("productos")

        else:
            # Si es una EDICION
            if id_producto:
                editar_producto(
                    id_producto, nombre_producto, categoria, precio, cantidad, True
                )
                messages.success(request, "Producto editado correctamente")

            # Si es un NUEVO producto
            else:
                nuevo_producto(nombre_producto, categoria, precio, cantidad)
                messages.success(request, "Producto agregado correctamente")

        return redirect("productos")

    # Parámetros de búsqueda y filtrado
    q = request.GET.get("q", "")
    categoria_filtrada = request.GET.get("categoria", "")

    productos = Producto.objects.filter(activo=True)

    if q:
        if q.isdigit():
            # Si es solo números, busco por ID (exacto o que contenga)
            productos = productos.filter(id__icontains=q)
        else:
            # Si no, buscamos por nombre
            productos = productos.filter(nombre__icontains=q)

    if categoria_filtrada:
        productos = productos.filter(categoria=categoria_filtrada)

    productos = productos.order_by("nombre")

    # Cargo de a 5 productos
    paginator_productos = Paginator(productos, 5)
    pagina_numero = request.GET.get("page")
    pagina_obj = paginator_productos.get_page(pagina_numero)

    contexto = {"productos": pagina_obj, "q": q, "categoria": categoria_filtrada}

    # Si es una petición AJAX, devuelvo solo la tabla
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "tabla_productos.html", contexto)

    return render(request, "productos.html", contexto)


@login_required
def clientes(request):
    if request.method == "POST":
        id_cliente = request.POST.get("id_cliente")
        nombre_cliente = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        telefono = request.POST.get("telefono")
        localidad = request.POST.get("localidad")
        direccion = request.POST.get("direccion")
        # El checkbox llega como 'on' si está marcado, lo convierto en un booleano
        factura = request.POST.get("factura") == "on"
        cuit = request.POST.get("cuit")
        if not factura:
            cuit = None
        elif cuit:
            # Elimina todos los guiones antes de guardarlo en la base de datos
            cuit = cuit.replace("-", "")

        # Si es una ELIMINACION, aqui traigo el id a borrar
        id_eliminar = request.POST.get("id_eliminar")
        if id_eliminar:
            eliminar_cliente(id_eliminar)
            messages.success(request, "Cliente eliminado correctamente")
            return redirect("clientes")

        else:
            # Si es una EDICION
            if id_cliente:
                editar_cliente(
                    id_cliente,
                    nombre_cliente,
                    apellido,
                    telefono,
                    localidad,
                    direccion,
                    factura,
                    cuit,
                    True,
                )
                messages.success(request, "Cliente editado correctamente")

            # Si es un NUEVO cliente
            else:
                nuevo_cliente(
                    nombre_cliente,
                    apellido,
                    telefono,
                    localidad,
                    direccion,
                    factura,
                    cuit,
                )
                messages.success(request, "Cliente agregado correctamente")

        return redirect("clientes")

    # Parámetros de búsqueda
    q = request.GET.get("q", "")

    clientes_list = Cliente.objects.filter(activo=True)

    if q:
        if q.isdigit():
            # Si es solo números, busco por ID (exacto o que contenga)
            clientes_list = clientes_list.filter(id__icontains=q)
        else:
            # Buscar por nombre o apellido
            from django.db.models import Q

            clientes_list = clientes_list.filter(
                Q(nombre__icontains=q) | Q(apellido__icontains=q)
            )

    clientes_list = clientes_list.order_by("nombre")

    # Cargo de a 5 clientes
    paginator_clientes = Paginator(clientes_list, 5)
    pagina_numero = request.GET.get("page")
    pagina_obj = paginator_clientes.get_page(pagina_numero)

    contexto = {"clientes": pagina_obj, "q": q}

    # Si es AJAX, devolvemos el parcial
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "tabla_clientes.html", contexto)

    return render(request, "clientes.html", contexto)


@login_required()
def informacion_clientes(request, id_cliente):
    cliente = get_object_or_404(Cliente, id=id_cliente, activo=True)
    return render(request, "informacion_clientes.html", {"cliente": cliente})


@login_required()
def operaciones(request, id_cliente):
    cliente = get_object_or_404(Cliente, id=id_cliente)

    productos = Producto.objects.filter(activo=True).order_by("nombre")

    # Cargo de a 6 productos para tener un alto de tabla acorde
    paginator_productos = Paginator(productos, 6)
    pagina_numero = request.GET.get("page")
    pagina_obj = paginator_productos.get_page(pagina_numero)

    contexto = {"cliente": cliente, "productos": pagina_obj}

    return render(request, "operaciones.html", contexto)


# Verifico que solo un administrador pueda ver la vista, tambien verifica que el usuario este logueado
@staff_member_required(login_url="inicio")
def deudores(request):
    return render(request, "deudores.html")


@login_required
def remitos(request):
    return render(request, "remitos.html")


@login_required
def obtener_cliente_json(request, id_cliente):
    from django.http import JsonResponse
    from .services import obtener_datos_cliente

    # Obtengo los datos ya procesados y filtrados
    datos = obtener_datos_cliente(id_cliente)

    if datos:
        # Si el cliente existe y está activo, devuelvo sus datos en formato JSON
        return JsonResponse(datos)

    # Si el servicio me devuelve None (cliente no encontrado o inactivo), respondo con un error 404
    return JsonResponse({"Error": "Cliente no encontrado"}, status=404)


@login_required
def obtener_producto_json(request, id_producto):
    from django.http import JsonResponse
    from .services import obtener_datos_producto

    datos = obtener_datos_producto(id_producto)

    if datos:
        # Si el producto existe, devuelvo la respuesta exitosa en JSON
        return JsonResponse(datos)

    # Si no lo encuentro o está inactivo, devuelvo un error 404
    return JsonResponse({"Error": "Producto no encontrado"}, status=404)


def cerrar_sesion(request):
    auth_logout(request)
    return redirect("login")
