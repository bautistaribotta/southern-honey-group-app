from django.db import models


class Producto(models.Model):
    categorias = [
        ('Miel', 'Miel'),
        ('Alimento', 'Alimento'),
        ('Cera', 'Cera'),
        ('Madera', 'Madera'),
        ('Estampa', 'Estampa'),
        ('Insumos', 'Insumos'),
        ('Medicamentos', 'Medicamentos'),
        ('Otros', 'Otros'),
    ]
    nombre = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50, choices=categorias, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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
        db_table = 'productos'

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
        db_table = 'clientes'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Operacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.CharField(max_length=200, null=True, blank=True)
    monto_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    metodo_de_pago = models.CharField(max_length=50)
    valor_dolar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_kilo_miel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Obligo a Django a nombrar la tabla como "operaciones"
    class Meta:
        db_table = 'operaciones'

    def __str__(self):
        return f"Operación {self.id} - {self.cliente}"


class DetalleOperacion(models.Model):
    operacion = models.ForeignKey(Operacion, on_delete=models.CASCADE, db_column='id_operacion')
    # Usamos PROTECT para evitar que el borrado de un producto elimine registros históricos de ventas
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, db_column='id_producto')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    # Obligo a Django a nombrar la tabla como "detalle_operaciones"
    class Meta:
        db_table = 'detalle_operaciones'
        # Sintaxis moderna para asegurar que un producto no se repita en la misma operación
        constraints = [
            models.UniqueConstraint(fields=['operacion', 'producto'], name='unique_operacion_producto')
        ]

    def __str__(self):
        return f"{self.cantidad} de {self.producto} (Op: {self.operacion.id})"


class Remito(models.Model):
    pass


class Pagos(models.Model):
    pass