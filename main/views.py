from .services import (get_cotizacion_oficial, get_cotizacion_blue,
                       get_cotizacion_miel_clara, get_cotizacion_miel_oscura,
                       nuevo_producto, nuevo_cliente, editar_producto, editar_cliente)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Producto, Cliente


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
    contexto = {
        "oficial": dolar_oficial,
        "blue": dolar_blue
    }
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

        if id_producto:
            editar_producto(id_producto, nombre_producto, categoria, precio, cantidad, activo)

        else:
            nuevo_producto(nombre_producto, categoria, precio, cantidad)
            messages.success(request, "Producto agregado correctamente.")

        return redirect("productos")

    # Parámetros de búsqueda y filtrado
    q = request.GET.get("q", "")
    categoria_filtrada = request.GET.get("categoria", "")
    
    productos = Producto.objects.filter(activo=True)
    
    if q:
        if q[0].isdigit():
            # Si inicia con números, buscamos por ID (exacto o que contenga)
            productos = productos.filter(id__icontains=q)
        else:
            # Si no, buscamos por nombre
            productos = productos.filter(nombre__icontains=q)
            
    if categoria_filtrada:
        productos = productos.filter(categoria=categoria_filtrada)
        
    productos = productos.order_by("nombre")

    paginator_productos = Paginator(productos, 5)
    pagina_numero = request.GET.get("page")
    pagina_obj = paginator_productos.get_page(pagina_numero)

    contexto = {
        "productos": pagina_obj,
        "q": q,
        "categoria": categoria_filtrada
    }

    # Si es una petición AJAX, devolvemos solo la tabla
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
        factura = request.POST.get("factura")
        cuit = request.POST.get("cuit")

        if id_cliente:
            editar_cliente(id_cliente)

        else:
            nuevo_cliente(nombre_cliente, apellido, telefono, localidad, direccion, factura, cuit)
            messages.success(request, "Cliente creado correctamente")

        return redirect("clientes")

    """
    1-Trae solo los clientes activos de la base de datos ordenados por nombre
    2-Divide esa lista total en bloques de 5 clientes
    3-Se fija en la URL en qué página está el usuario
    4-Extraigo únicamente los 5 clientes que corresponden a esa página específica
      para no ralentizar la busqueda si tengo muchos elementos en la base de datos
    """
    clientes = Cliente.objects.filter(activo=True).order_by("nombre")
    paginator_clientes = Paginator(clientes, 5)
    pagina_numero = request.GET.get("page")
    pagina_obj = paginator_clientes.get_page(pagina_numero)

    return render(request, "clientes.html", {"clientes": pagina_obj})


@login_required
def deudores(request):
    return render(request, "deudores.html")


@login_required
def remitos(request):
    return render(request, "remitos.html")


def cerrar_sesion(request):
    auth_logout(request)
    return redirect("login")