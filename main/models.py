from django.db import models
from django.db.models import Sum, F, Subquery, OuterRef, DecimalField, Value
from django.db.models.functions import Coalesce


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


class OperacionQuerySet(models.QuerySet):
    def con_totales(self):
        """
        Anota el monto total (suma de detalles) y el total pagado en una sola query,
        evitando el N+1 que generan las properties monto_total/total_pagado al iterar
        sobre un listado. Uso subqueries separadas para no sufrir el fan-out que
        multiplicaria los montos al combinar dos agregaciones por JOIN.
        """
        monto_detalles = (
            DetalleOperacion.objects.filter(operacion=OuterRef("pk"))
            .values("operacion")
            .annotate(total=Sum(F("cantidad") * F("precio_unitario")))
            .values("total")
        )
        monto_pagos = (
            Pago.objects.filter(operacion=OuterRef("pk"))
            .values("operacion")
            .annotate(total=Sum("monto"))
            .values("total")
        )
        return self.annotate(
            _monto_total_anotado=Coalesce(
                Subquery(monto_detalles, output_field=DecimalField()),
                Value(0),
                output_field=DecimalField(),
            ),
            _total_pagado_anotado=Coalesce(
                Subquery(monto_pagos, output_field=DecimalField()),
                Value(0),
                output_field=DecimalField(),
            ),
        )


class Operacion(models.Model):
    TIPO_OPERACION = [
        ("compra", "Compra"),
        ("venta", "Venta"),
    ]

    objects = OperacionQuerySet.as_manager()

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
        # Si el queryset vino anotado con con_totales(), uso el valor ya calculado
        # para no disparar una query por cada operacion del listado.
        if hasattr(self, "_monto_total_anotado"):
            return self._monto_total_anotado or 0
        resultado = self.detalleoperacion_set.aggregate(
            total=Sum(F('cantidad') * F('precio_unitario'))
        )['total']
        return resultado if resultado is not None else 0

    @property
    def total_pagado(self):
        if hasattr(self, "_total_pagado_anotado"):
            return self._total_pagado_anotado or 0
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

    @property
    def total_viajes(self):
        # Cantidad de viajes activos del chofer. Un viaje cuenta como uno,
        # sin importar cuantos destinos tenga. Si el queryset vino anotado con
        # _num_viajes (ver obtener_choferes_activos) reutilizo ese valor para
        # evitar una query por fila en el listado de flota.
        if hasattr(self, "_num_viajes"):
            return self._num_viajes
        return self.viaje_set.filter(activo=True).count()

    def __str__(self):
        return f"Chofer: {self.nombre} {self.apellido}"


class Vehiculo(models.Model):
    nombre = models.CharField(max_length=30)
    patente = models.CharField(max_length=7, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "vehiculos"

    @property
    def total_viajes(self):
        if hasattr(self, "_num_viajes"):
            return self._num_viajes
        return self.viaje_set.filter(activo=True).count()

    def __str__(self):
        return f"Vehiculo {self.nombre} ({self.patente})"


class Viaje(models.Model):
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


class ViajeReparto(models.Model):
    fecha_viaje_reparto = models.DateField()
    chofer = models.ForeignKey(Chofer, on_delete=models.PROTECT, db_column="id_chofer")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, db_column="id_vehiculo")
    gasto_combustible_viaje_reparto = models.IntegerField(default=0)
    costo_empleado = models.IntegerField(default=0)
    valor_viaje = models.IntegerField(default=0)

    class Meta:
        db_table = "viaje_reparto"

    # Calculo la ganancia como el valor del viaje - combustible - nomina empleado
    @property
    def ganancia(self):
        return self.valor_viaje - self.gasto_combustible_viaje_reparto - self.costo_empleado

    def __str__(self):
        return f"Viaje reparto nro: {self.id}"


class DetalleViajeReparto(models.Model):
    viaje_reparto = models.ForeignKey(ViajeReparto, on_delete=models.CASCADE,
                                      related_name="destinos", db_column="id_viajereparto")
    destinos_reparto = models.CharField(max_length=30)

    class Meta:
        db_table = "detalle_viaje_reparto"

    def __str__(self):
        return f"Destino {self.destinos_reparto} del {self.viaje_reparto}"