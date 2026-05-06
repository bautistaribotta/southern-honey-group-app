from django.contrib import admin
from .models import Cliente, Producto, Operacion, DetalleOperacion, Pago, Cotizaciones

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Pago)
admin.site.register(Cotizaciones)


class DetalleOperacionInline(admin.TabularInline):
    model = DetalleOperacion
    extra = 1


@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):
    inlines = [DetalleOperacionInline]
