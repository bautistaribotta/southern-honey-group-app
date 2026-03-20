from django.urls import path
from main.views import login, inicio, productos, clientes, deudores, remitos, cerrar_sesion, informacion_clientes

"""
La sentencia name="nombre_del_archivo" se usa 
para que Django sepa la ruta relativa del .html
"""
urlpatterns = [
    path('', login, name="login"),
    path('inicio/', inicio, name="inicio"),
    path('productos/', productos, name="productos"),
    path('clientes/', clientes, name="clientes"),
    path('informacion_clientes', informacion_clientes, name="informacion_clientes"),
    path('deudores/', deudores, name="deudores"),
    path('remitos/', remitos, name="remitos"),
    path('cerrar_sesion', cerrar_sesion, name="cerrar_sesion")
]