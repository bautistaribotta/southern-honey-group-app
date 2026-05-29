from django.contrib import admin
from .models import Cliente, Producto, Operacion, DetalleOperacion, Pago, Cotizaciones, Chofer, Vehiculo, Viaje, DetalleViaje

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Pago)
admin.site.register(Cotizaciones)
admin.site.register(Chofer)
admin.site.register(Vehiculo)

class DetalleOperacionInline(admin.TabularInline):
    model = DetalleOperacion
    extra = 1

@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):
    inlines = [DetalleOperacionInline]

class DetalleViajeInline(admin.TabularInline):
    model = DetalleViaje
    extra = 1

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    inlines = [DetalleViajeInline]
    list_display = ('id', 'chofer', 'vehiculo', 'fecha_inicio', 'fecha_vuelta')
