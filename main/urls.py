from django.urls import path
from main.views import (login, inicio, actualizar_cotizacion_ajax,
                        productos, clientes, informacion_clientes, informacion_operacion, generar_remito,
                        operaciones, cancelar_operacion, registrar_pago, obtener_cliente_json,
                        obtener_producto_json, viajes, informacion_viaje, deudores, mercado_libre, cerrar_sesion)

"""
La sentencia name="nombre_del_archivo" se usa 
para que Django sepa la ruta relativa del .html
"""
urlpatterns = [
    path('', login, name="login"),
    path('inicio/', inicio, name="inicio"),
    path('actualizar_cotizacion/', actualizar_cotizacion_ajax, name="actualizar_cotizacion"),
    path('productos/', productos, name="productos"),
    path('clientes/', clientes, name="clientes"),
    path('informacion_clientes/<int:id_cliente>/', informacion_clientes, name="informacion_clientes"),
    path('informacion_operacion/<int:id_operacion>/', informacion_operacion, name="informacion_operacion"),
    path('generar_remito/<int:id_operacion>/', generar_remito, name="generar_remito"),
    path('cancelar_operacion/<int:id_operacion>/', cancelar_operacion, name="cancelar_operacion"),
    path('registrar_pago/<int:id_operacion>/', registrar_pago, name="registrar_pago"),
    path('operaciones/<int:id_cliente>/', operaciones, name="operaciones"),
    path('api/clientes/<int:id_cliente>/', obtener_cliente_json, name="obtener_cliente_json"),
    path('api/productos/<int:id_producto>/', obtener_producto_json, name="obtener_producto_json"),
    path('viajes/', viajes, name="viajes"),
    path('informacion_viaje/<int:id_viaje>/', informacion_viaje, name="informacion_viaje"),
    path('deudores/', deudores, name="deudores"),
    path('mercado_libre/', mercado_libre, name="mercado_libre"),
    path('cerrar_sesion', cerrar_sesion, name="cerrar_sesion")
]