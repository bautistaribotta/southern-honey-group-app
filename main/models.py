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
    cantidad_comprada = models.PositiveIntegerField(default=0)
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
    TIPO_OPERACION = [
        ("compra", "Compra"),
        ("venta", "Venta"),
    ]

    # Como la tabla viaje esta definida mas abajo, coloco el nombre entre comillas para que Django la lea antes
    viaje = models.ForeignKey("Viaje", on_delete=models.SET_NULL, null=True,
                              blank=True, related_name="operaciones", db_column="id_viaje")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, db_column="id_cliente")
    fecha = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    tipo_operacion = models.CharField(max_length=10, choices=TIPO_OPERACION)
    valor_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_kilo_miel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Obligo a Django a nombrar la tabla como "operaciones"
    class Meta:
        db_table = "operaciones"
        verbose_name_plural = "Operaciones"

    @property
    def monto_total(self):
        from django.db.models import Sum, F
        resultado = self.detalleoperacion_set.aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'))
        )['total']
        return resultado if resultado is not None else 0

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
        elif pagado >= self.monto_total:
            return "Pagada"
        else:
            return "Pago Parcial"

    def __str__(self):
        return f"Operación {self.id} - {self.cliente}"


class DetalleOperacion(models.Model):
    operacion = models.ForeignKey(Operacion, on_delete=models.CASCADE, db_column="id_operacion")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column="id_producto")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

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
    monto = models.IntegerField(default=1)

    class Meta:
        db_table = "cotizaciones"
        verbose_name_plural = "Cotizaciones"

    def __str__(self):
        return f"Cotizacion {self.articulo}: {self.monto}"


class Chofer(models.Model):
    nombre = models.CharField(max_length=25)
    apellido = models.CharField(max_length=25)
    total_viajes = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "choferes"
        verbose_name_plural = "Choferes"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "apellido"],
                name="unique_nombre_apellido_chofer"
            )
        ]

    def __str__(self):
        return f"Chofer: {self.nombre} {self.apellido}"


class Vehiculo(models.Model):
    nombre = models.CharField(max_length=30)
    patente = models.CharField(max_length=7, unique=True)
    total_viajes = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "vehiculos"

    def __str__(self):
        return f"Vehiculo"


class Viaje(models.Model):
    # TODO: LLAVES FORANEAS ¿Remitos/Operaciones? YA DEFINIDA, VINCULAR
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT, db_column="id_chofer")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, db_column="id_vehiculo")
    inicio_caja = models.IntegerField(default=0)
    fecha_inicio = models.DateField()
    fecha_vuelta = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    @property
    def total_gastos(self) -> int:
        from django.db.models import Sum

        # Suma todos los montos de la tabla Gasto asociados a este viaje
        resultado = self.detalle_gastos.aggregate(total=Sum('monto'))['total']
        if resultado is not None:
            return resultado
        else:
            return 0

    @property
    def final_caja(self) -> int:
        return int(self.inicio_caja) - self.total_gastos

    @property
    def estado(self):
        from django.utils import timezone
        if self.fecha_vuelta:
            hoy = timezone.localdate()
            if hoy > self.fecha_vuelta:
                return "Finalizado"
        return "En curso"

    class Meta:
        db_table = "viajes"

    def __str__(self):
        return f"viaje {self.id}"


class DetalleViaje(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name="destinos", db_column="id_viaje")
    destino = models.CharField(max_length=30)

    class Meta:
        db_table = "detalle_viajes"

    def __str__(self):
        return f"Destino {self.destino} (Viaje {self.viaje_id})"


class Gasto(models.Model):
    TIPO_GASTOS = [
        ("Comida", "Comida"),
        ("Combustible", "Combustible"),
        ("Playa", "Playa"),
        ("Peaje", "Peaje"),
        ("Hotel", "Hotel"),
        ("Viaticos personales", "Viaticos personales"),
        ("Extras", "Extras")
    ]
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name="detalle_gastos", db_column="id_viaje")
    gasto = models.CharField(choices=TIPO_GASTOS, max_length=25)
    monto = models.IntegerField(default=0)
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "gastos"

    def __str__(self):
        return f"Gasto {self.gasto} de {self.monto} pesos (Viaje: {self.viaje})"
