from .services import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.admin.views.decorators import staff_member_required
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
            editar_producto(id_producto, nombre_producto, categoria, precio, cantidad, True)
            messages.success(request, "Producto editado correctamente.")

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

    # Cargo de a 5 productos
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
        # El checkbox llega como 'on' si está marcado, lo convierto en un booleano
        factura = request.POST.get("factura") == 'on'
        cuit = request.POST.get("cuit")

        if id_cliente:
            editar_cliente(id_cliente, nombre_cliente, apellido, telefono, localidad, direccion, cuit, factura, True)
            messages.success(request, "Cliente editado correctamente")

        else:
            nuevo_cliente(nombre_cliente, apellido, telefono, localidad, direccion, cuit, factura)
            messages.success(request, "Cliente agregado correctamente")

        return redirect("clientes")

    # Parámetros de búsqueda
    q = request.GET.get("q", "")
    
    clientes_list = Cliente.objects.filter(activo=True)
    
    if q:
        if q[0].isdigit():
            # Buscar por ID si empieza con número
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

    contexto = {
        "clientes": pagina_obj,
        "q": q
    }

    # Si es AJAX, devolvemos el parcial
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "tabla_clientes.html", contexto)

    return render(request, "clientes.html", contexto)


@login_required()
def informacion_clientes(request):
    return render(request, "informacion_clientes.html")


# Verifico que solo un administrador pueda ver la vista, tambien verifica que el usuario este logueado
@staff_member_required(login_url="inicio")
def deudores(request):
    return render(request, "deudores.html")


@login_required
def remitos(request):
    return render(request, "remitos.html")


def cerrar_sesion(request):
    auth_logout(request)
    return redirect("login")