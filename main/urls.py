from django.urls import path
from main.views import (login, inicio,
                        productos, clientes,
                        informacion_clientes, informacion_operaciones, operaciones,
                        obtener_cliente_json, obtener_producto_json,
                        deudores, cerrar_sesion, cancelar_operacion, registrar_pago)

"""
La sentencia name="nombre_del_archivo" se usa 
para que Django sepa la ruta relativa del .html
"""
urlpatterns = [
    path('', login, name="login"),
    path('inicio/', inicio, name="inicio"),
    path('productos/', productos, name="productos"),
    path('clientes/', clientes, name="clientes"),
    path('informacion_clientes/<int:id_cliente>/', informacion_clientes, name="informacion_clientes"),
    path('informacion_operaciones/<int:id_operacion>/', informacion_operaciones, name="informacion_operaciones"),
    path('cancelar_operacion/<int:id_operacion>/', cancelar_operacion, name="cancelar_operacion"),
    path('registrar_pago/<int:id_operacion>/', registrar_pago, name="registrar_pago"),
    path('operaciones/<int:id_cliente>/', operaciones, name="operaciones"),
    path('api/clientes/<int:id_cliente>/', obtener_cliente_json, name="obtener_cliente_json"),
    path('api/productos/<int:id_producto>/', obtener_producto_json, name="obtener_producto_json"),
    path('deudores/', deudores, name="deudores"),
    path('cerrar_sesion', cerrar_sesion, name="cerrar_sesion")
]