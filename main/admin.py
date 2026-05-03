from django.contrib import admin
from .models import Cliente, Producto, Operacion, DetalleOperacion, Pago

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Pago)


class DetalleOperacionInline(admin.TabularInline):
    model = DetalleOperacion
    extra = 1


@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):
    inlines = [DetalleOperacionInline]
