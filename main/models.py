from dataclasses import field, fields

from django.db import models


class Producto(models.Model):
    categorias = [
        ("Miel", "Miel"),
        ("Alimento", "Alimento"),
        ("Cera", "Cera"),
        ("Madera", "Madera"),
        ("Estampado", "Estampado"),
        ("Insumos", "Insumos"),
        ("Medicamentos", "Medicamentos"),
        ("Otros", "Otros"),
    ]
    nombre = models.CharField(max_length=50, unique=True)
    categoria = models.CharField(max_length=50, choices=categorias, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    cantidad_vendida = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    """
        En sistemas comerciales, es mejor usar un campo 'activo' en lugar de borrar 
        productos físicamente. Si borro un producto, podría perder el historial de ventas.
        Al usar 'activo=False', el producto deja de mostrarse en la interfaz pero los registros históricos
        en 'detalle_operaciones' permanecen intactos
    """

    # Obligo a Django a nombrar la tabla como "productos"
    class Meta:
        db_table = "productos"

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    localidad = models.CharField(max_length=50, null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    factura_produccion = models.BooleanField(default=False)
    cuit = models.CharField(max_length=15, null=True, blank=True)
    activo = models.BooleanField(default=True)

    # Obligo a Django a nombrar la tabla como "clientes"
    class Meta:
        db_table = "clientes"

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Operacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column="id_cliente")
    fecha = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    observaciones = models.CharField(max_length=200, null=True, blank=True)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_kilo_miel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Obligo a Django a nombrar la tabla como "operaciones"
    class Meta:
        db_table = "operaciones"
        verbose_name_plural = "Operaciones"

    @property
    def total_pagado(self):
        from django.db.models import Sum
        return self.pago_set.aggregate(total=Sum('monto'))['total'] or 0

    @property
    def estado_pago(self):
        if not self.activa:
            return "Cancelada"
        
        pagado = self.total_pagado
        
        if pagado == 0:
            return "Debe"
        elif pagado >= (self.monto_total or 0):
            return "Pagada"
        else:
            return "Pago Parcial"

    def __str__(self):
        return f"Operación {self.id} - {self.cliente}"


class DetalleOperacion(models.Model):
    operacion = models.ForeignKey(Operacion, on_delete=models.CASCADE, db_column="id_operacion")
    # Usamos PROTECT para evitar que el borrado de un producto elimine registros históricos de ventas
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_producto")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    # Obligo a Django a nombrar la tabla como "detalle_operaciones"
    class Meta:
        db_table = "detalle_operaciones"
        # Sintaxis moderna para asegurar que un producto no se repita en la misma operación
        constraints = [
            models.UniqueConstraint(
                fields=["operacion", "producto"], name="unique_operacion_producto"
            )
        ]

    def __str__(self):
        return f"{self.cantidad} de {self.producto} (Op: {self.operacion.id})"


class Pago(models.Model):
    operacion = models.ForeignKey(Operacion, on_delete=models.CASCADE, db_column="id_operacion")
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = "pagos"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago de la operacion: {self.operacion}"


class Cotizaciones(models.Model):
    articulo = models.CharField(max_length=25, unique=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = "cotizaciones"

    def __str__(self):
        return f"Cotizacion {self.articulo}: {self.monto}"


class Chofer(models.Model):
    nombre = models.CharField(max_length=25)
    apellido = models.CharField(max_length=25)
    total_viajes = models.IntegerField(default=0)

    class Meta:
        db_table = "choferes"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "apellido"],
                name="unique_nombre_apellido_chofer"
            )
        ]

    def __str__(self):
        return f"Chofer: {self.nombre}"


class Vehiculo(models.Model):
    nombre = models.CharField(max_length=30)
    patente = models.CharField(max_length=7)
    total_viajes = models.IntegerField(default=0)

    class Meta:
        db_table = "vehiculos"

    def __str__(self):
        return f"Vehiculo"


class Viaje(models.Model):
    # TODO: LLAVES FORANEAS ¿Remitos?
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    inicio_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_vuelta = models.DateTimeField(null=True, blank=True)
    gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "viajes"

    def __str__(self):
        return f"viaje {self.id}"