"""
Carga datos de prueba para la demostracion del sistema.

Pensado para la instalacion de PythonAnywhere, que corre contra una base
separada de la real. El comando solo inserta: nunca borra ni modifica lo que ya
estaba, asi que se puede correr sobre una base recien migrada sin perder nada.

Los numeros salen de random con semilla fija: dos corridas con la misma semilla
generan exactamente los mismos datos, asi la demo es reproducible y se puede
volver a armar igual si hay que rehacer la base.

    python manage.py cargar_datos_demo --si

No genera Alquileres ni IVA: esas secciones no se publican en esta instalacion
(ver la nota en urls.py), asi que cargarlas seria llenar tablas que nadie ve.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from main.models import (
    Banco, CargaCombustible, Cheque, Cliente, CuentaCorriente, DestinoViajeReparto,
    DetalleOperacion, DetalleViaje, DetalleViajeCereal, DetalleViajeReparto, Empleado,
    Empresa, EstacionDeServicio, Gasto, GastoViajeCereal, GastoViajeReparto, IngresoCaja,
    ObservacionVehiculo, Operacion, Pago, PagosEmpleados, Producto, ProductoPorKg,
    RegistroKilometraje, Seguro, Servis, Vehiculo, Viaje, ViajeCereal, ViajeReparto, VTV,
)

NOMBRES = [
    "Juan", "Maria", "Carlos", "Ana", "Jorge", "Lucia", "Miguel", "Sofia", "Raul",
    "Valeria", "Diego", "Marta", "Hector", "Elena", "Ruben", "Silvia", "Pablo",
    "Gabriela", "Osvaldo", "Claudia", "Ariel", "Natalia", "Fabian", "Roxana",
]
APELLIDOS = [
    "Gomez", "Fernandez", "Lopez", "Martinez", "Sosa", "Romero", "Alvarez", "Benitez",
    "Quiroga", "Ledesma", "Peralta", "Moyano", "Ibarra", "Cabrera", "Aguirre",
    "Villalba", "Ferreyra", "Bustos", "Ojeda", "Maldonado", "Correa", "Vera",
]
LOCALIDADES = [
    "General Pico", "Santa Rosa", "Trenque Lauquen", "Realico", "Eduardo Castex",
    "Intendente Alvear", "Rio Cuarto", "Villa Maria", "Pergamino", "Junin",
    "America", "Bolivar", "Daireaux", "Carlos Casares", "Nueve de Julio",
]
CALLES = ["San Martin", "Belgrano", "Rivadavia", "Sarmiento", "Mitre", "Alsina", "Moreno"]


class Command(BaseCommand):
    help = "Carga datos de prueba para la demostracion (solo inserta, no borra)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--si", action="store_true",
            help="Confirma la carga. Sin este flag el comando no escribe nada.",
        )
        parser.add_argument(
            "--forzar", action="store_true",
            help="Carga aunque la base ya tenga operaciones cargadas.",
        )
        parser.add_argument(
            "--semilla", type=int, default=2026,
            help="Semilla del generador. Misma semilla, mismos datos.",
        )

    def handle(self, *args, **opciones):
        base = settings.DATABASES["default"]
        destino = f"{base.get('NAME')} en {base.get('HOST') or 'local'}"

        if not opciones["si"]:
            raise CommandError(
                f"Esto va a insertar datos de prueba en: {destino}\n"
                "Verifica que NO sea la base del sistema real y volve a correrlo "
                "con --si para confirmar."
            )

        ya_cargadas = Operacion.objects.count()
        if ya_cargadas and not opciones["forzar"]:
            raise CommandError(
                f"La base {destino} ya tiene {ya_cargadas} operaciones.\n"
                "Si igual queres agregar los datos de prueba encima, agrega --forzar."
            )

        azar = random.Random(opciones["semilla"])
        hoy = timezone.localdate()

        self.stdout.write(f"Cargando datos de prueba en {destino}...")

        with transaction.atomic():
            granel = self._articulos_granel(azar)
            productos = self._productos(azar)
            clientes = self._clientes(azar)
            empleados = self._empleados(azar, hoy)
            vehiculos = self._vehiculos(azar, hoy)
            self._operaciones(azar, clientes, productos, granel)
            self._viajes_miel(azar, hoy, empleados, vehiculos)
            self._viajes_reparto(azar, hoy, empleados, vehiculos)
            self._viajes_cereales(azar, hoy, empleados, vehiculos, clientes)
            self._combustible(azar, hoy, empleados, vehiculos)
            self._cheques(azar, hoy)
            self._pagos_empleados(azar, hoy, empleados)

        self.stdout.write(self.style.SUCCESS("Listo. Resumen de la base:"))
        for etiqueta, modelo in (
            ("Clientes", Cliente), ("Productos", Producto), ("Articulos por kg", ProductoPorKg),
            ("Empleados", Empleado), ("Vehiculos", Vehiculo), ("Operaciones", Operacion),
            ("Pagos", Pago), ("Viajes miel/cera", Viaje), ("Viajes reparto", ViajeReparto),
            ("Viajes cereales", ViajeCereal), ("Cargas de combustible", CargaCombustible),
            ("Cheques", Cheque),
        ):
            self.stdout.write(f"  {etiqueta}: {modelo.objects.count()}")

    # ---------------------------------------------------------------- catalogos

    def _articulos_granel(self, azar):
        """
        Los articulos de cotizacion ya existen por migracion: aca solo les pongo
        precio y kilos para que el tablero de inicio no muestre todo en cero.
        """
        precios = {
            "Miel menor a 34 mm": 3200, "Miel menor a 50 mm": 3050,
            "Miel mayor a 50 mm": 2850, "Cera Operculo": 9800,
            "Cera Recupero": 6400, "Cera Borra de Operculo": 4100,
        }
        articulos = []
        for nombre, precio in precios.items():
            categoria = "Miel" if nombre.startswith("Miel") else "Cera"
            articulo, _ = ProductoPorKg.objects.get_or_create(
                articulo=nombre,
                defaults={"categoria": categoria, "activo": True, "mostrar_en_inicio": True},
            )
            articulo.monto = precio
            articulo.cantidad = Decimal(azar.randrange(1_200, 18_000)) + Decimal("0.50")
            articulo.mostrar_en_inicio = True
            articulo.save()
            articulos.append(articulo)
        return articulos

    def _productos(self, azar):
        """
        Productos por unidad. Los tambores vacios nacen marcados para inicio: es
        la tarjeta que acompana a la miel en el tablero.
        """
        catalogo = [
            ("Miel fraccionada 500g", "Miel", 4200), ("Miel fraccionada 1kg", "Miel", 7800),
            ("Alimento energetico 5kg", "Alimento", 9500), ("Alimento proteico 10kg", "Alimento", 21000),
            ("Cera estampada 60x40", "Estampado", 15800), ("Cera estampada 45x20", "Estampado", 9200),
            ("Cuadro de madera", "Madera", 1750), ("Alza media melaria", "Madera", 18500),
            ("Camara de cria", "Madera", 26400), ("Piso sanitario", "Madera", 8900),
            ("Techo chapa galvanizada", "Madera", 12300), ("Ahumador inoxidable", "Insumos", 24500),
            ("Palanca desoperculadora", "Insumos", 8600), ("Traje completo tipo astronauta", "Insumos", 68000),
            ("Guantes de cuero", "Insumos", 14200), ("Nucleo poliestireno", "Insumos", 31000),
            ("Amitraz tiras x10", "Medicamentos", 11800), ("Oxalico 100g", "Medicamentos", 6400),
            ("Timol 500g", "Medicamentos", 15600), ("Tambor 300 lts reacondicionado", "Tambores Vacios", 42000),
            ("Tambor 200 lts usado", "Tambores Vacios", 28000), ("Tambor nuevo con tapa", "Tambores Vacios", 61000),
            ("Baldes 25 lts", "Otros", 5400), ("Etiquetas autoadhesivas x100", "Otros", 3900),
        ]
        productos = []
        for nombre, categoria, precio in catalogo:
            vendida = azar.randrange(20, 400)
            comprada = vendida + azar.randrange(10, 260)
            producto, creado = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "categoria": categoria,
                    "precio": Decimal(precio),
                    "cantidad": comprada - vendida,
                    "cantidad_vendida": vendida,
                    "cantidad_comprada": comprada,
                    "activo": True,
                    "mostrar_en_inicio": categoria == "Tambores Vacios",
                },
            )
            if not creado and categoria == "Tambores Vacios" and not producto.mostrar_en_inicio:
                producto.mostrar_en_inicio = True
                producto.save(update_fields=["mostrar_en_inicio"])
            productos.append(producto)
        return productos

    def _clientes(self, azar):
        clientes = []
        for _ in range(40):
            clientes.append(Cliente.objects.create(
                nombre=azar.choice(NOMBRES),
                apellido=azar.choice(APELLIDOS),
                telefono=f"2302-{azar.randrange(400000, 699999)}",
                localidad=azar.choice(LOCALIDADES),
                direccion=f"{azar.choice(CALLES)} {azar.randrange(100, 3200)}",
                factura_produccion=azar.random() < 0.45,
                cuit=f"20-{azar.randrange(10_000_000, 44_999_999)}-{azar.randrange(0, 9)}",
                activo=azar.random() > 0.08,
            ))
        return clientes

    def _empleados(self, azar, hoy):
        empleados = []
        usados = set()
        while len(empleados) < 8:
            par = (azar.choice(NOMBRES), azar.choice(APELLIDOS))
            if par in usados:
                continue
            usados.add(par)
            empleados.append(Empleado.objects.create(
                nombre=par[0], apellido=par[1],
                sueldo=Decimal(azar.randrange(700_000, 1_450_000)),
                inicio_cuenta=hoy - timedelta(days=azar.randrange(200, 900)),
                # Reparto los vencimientos alrededor de hoy para que el semaforo
                # del listado muestre los tres estados: vencido, proximo y vigente
                vencimiento_carnet=hoy + timedelta(days=azar.randrange(-90, 700)),
                activo=True,
            ))
        return empleados

    def _vehiculos(self, azar, hoy):
        modelos = [
            "Iveco Tector", "Mercedes Benz 1620", "Ford Cargo 1722", "Scania P310",
            "Volkswagen Constellation", "Iveco Daily",
        ]
        vehiculos = []
        for modelo in modelos:
            letras = "".join(azar.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(2))
            vehiculo = Vehiculo.objects.create(
                nombre=modelo,
                patente=f"A{azar.randrange(100, 999)}{letras}",
                activo=True,
            )
            vehiculos.append(vehiculo)

            km = azar.randrange(180_000, 720_000)
            for mes in range(6, 0, -1):
                RegistroKilometraje.objects.create(
                    vehiculo=vehiculo,
                    fecha=hoy - timedelta(days=mes * 30),
                    kilometros=Decimal(km - mes * azar.randrange(2_000, 6_500)),
                )
            # Vencimientos escalonados: algunos vencidos, otros por vencer
            desfase = azar.randrange(-60, 300)
            Seguro.objects.create(
                vehiculo=vehiculo, inicio=hoy - timedelta(days=365 - desfase),
                fin=hoy + timedelta(days=desfase),
                costo=Decimal(azar.randrange(180_000, 460_000)),
                observaciones="Poliza anual todo riesgo",
            )
            VTV.objects.create(
                vehiculo=vehiculo, inicio=hoy - timedelta(days=365 - desfase // 2),
                fin=hoy + timedelta(days=desfase // 2),
                costo=Decimal(azar.randrange(45_000, 120_000)),
            )
            Servis.objects.create(
                vehiculo=vehiculo, fecha=hoy - timedelta(days=azar.randrange(20, 200)),
                costo=Decimal(azar.randrange(90_000, 380_000)),
                observaciones=azar.choice([
                    "Cambio de aceite y filtros", "Service de 20.000 km",
                    "Recambio de correas", "Alineacion y balanceo",
                ]),
            )
            ObservacionVehiculo.objects.create(
                vehiculo=vehiculo, fecha=hoy - timedelta(days=azar.randrange(5, 120)),
                texto=azar.choice([
                    "Perdida de aceite leve en el carter, revisar",
                    "Cubiertas traseras al limite, presupuestar recambio",
                    "Aire acondicionado no enfria",
                    "Golpe en el paragolpes delantero, sin urgencia",
                ]),
            )
        return vehiculos

    # ------------------------------------------------------------- operaciones

    def _operaciones(self, azar, clientes, productos, granel):
        """
        Mezcla ventas y compras a lo largo de 12 meses. Una parte queda sin
        pagar del todo a proposito: son las que alimentan la seccion de Deudas.
        """
        envasados = [p for p in productos if p.categoria != "Tambores Vacios"]
        ahora = timezone.now()

        for _ in range(150):
            fecha = ahora - timedelta(days=azar.randrange(0, 365), hours=azar.randrange(0, 23))
            operacion = Operacion.objects.create(
                cliente=azar.choice(clientes),
                fecha=fecha,
                tipo_operacion="venta" if azar.random() < 0.7 else "compra",
                valor_dolar=Decimal(azar.randrange(1_050, 1_480)),
                valor_kilo_miel=Decimal(azar.randrange(2_800, 3_400)),
                valor_kilo_cera=Decimal(azar.randrange(5_800, 10_200)),
                observaciones=azar.choice([
                    "", "", "", "Retira en deposito", "Entregar con remito",
                    "Pago acordado a 30 dias", "Cliente pidio factura A",
                ]),
                activa=True,
            )

            total = Decimal("0")
            # Lineas por unidad: sample evita repetir producto en la operacion,
            # que es lo que prohibe unique_operacion_producto
            for producto in azar.sample(envasados, azar.randrange(1, 4)):
                cantidad = Decimal(azar.randrange(1, 40))
                precio = producto.precio or Decimal(5000)
                DetalleOperacion.objects.create(
                    operacion=operacion, producto=producto,
                    cantidad=cantidad, precio_unitario=precio,
                )
                total += cantidad * precio

            # Lineas a granel: la mitad de las operaciones lleva miel o cera
            if azar.random() < 0.5:
                for articulo in azar.sample(granel, azar.randrange(1, 3)):
                    kilos = Decimal(azar.randrange(50, 2_400))
                    precio = Decimal(articulo.monto)
                    DetalleOperacion.objects.create(
                        operacion=operacion, cotizacion=articulo,
                        cantidad=kilos, precio_unitario=precio,
                    )
                    total += kilos * precio

            # Un 40% queda con saldo pendiente para que Deudas tenga que mostrar
            sorteo = azar.random()
            if sorteo < 0.6:
                pagado = total
            elif sorteo < 0.85:
                pagado = (total * Decimal(azar.randrange(20, 80)) / Decimal(100)).quantize(Decimal("0.01"))
            else:
                pagado = Decimal("0")

            if pagado > 0:
                Pago.objects.create(
                    operacion=operacion,
                    fecha=fecha + timedelta(days=azar.randrange(0, 25)),
                    monto=pagado,
                )

    # ------------------------------------------------------------------ viajes

    def _viajes_miel(self, azar, hoy, empleados, vehiculos):
        destinos = [
            "Santa Rosa", "General Pico", "Realico", "Rio Cuarto", "Villa Maria",
            "Trenque Lauquen", "Bolivar", "Junin", "Pergamino", "America",
        ]
        for _ in range(30):
            inicio = hoy - timedelta(days=azar.randrange(3, 360))
            caja = azar.randrange(300_000, 1_200_000)
            viaje = Viaje.objects.create(
                empleado=azar.choice(empleados),
                vehiculo=azar.choice(vehiculos),
                inicio_caja=caja,
                fecha_inicio=inicio,
                fecha_vuelta=inicio + timedelta(days=azar.randrange(1, 6)),
                activo=False,
            )
            for destino in azar.sample(destinos, azar.randrange(1, 4)):
                DetalleViaje.objects.create(viaje=viaje, destino=destino)

            gastado = 0
            for tipo in azar.sample([t[0] for t in Gasto.TIPO_GASTOS], azar.randrange(2, 6)):
                monto = azar.randrange(15_000, 180_000)
                gastado += monto
                Gasto.objects.create(viaje=viaje, gasto=tipo, monto=monto)

            if azar.random() < 0.4:
                IngresoCaja.objects.create(viaje=viaje, monto=azar.randrange(50_000, 400_000))

            # La devolucion del sobrante: registrada en la mayoria de los viajes
            sobrante = max(caja - gastado, 0)
            sorteo = azar.random()
            if sorteo < 0.6 and sobrante:
                viaje.devolucion_estado = Viaje.DEVOLUCION_TOTAL
                viaje.monto_devuelto = sobrante
                viaje.save(update_fields=["devolucion_estado", "monto_devuelto"])
            elif sorteo < 0.8 and sobrante:
                devuelto = sobrante // 2
                viaje.devolucion_estado = Viaje.DEVOLUCION_PARCIAL
                viaje.monto_devuelto = devuelto
                viaje.sobrante_devolucion = sobrante - devuelto
                viaje.save(update_fields=[
                    "devolucion_estado", "monto_devuelto", "sobrante_devolucion",
                ])

    def _viajes_reparto(self, azar, hoy, empleados, vehiculos):
        """
        El catalogo de destinos lo pobla la migracion 0049. Si la base viene
        vacia (por ejemplo si se limpio a mano) cargo algunos para que los
        viajes tengan a que apuntar.
        """
        destinos = list(DestinoViajeReparto.objects.filter(activo=True))
        if not destinos:
            for localidad in LOCALIDADES[:10]:
                destinos.append(DestinoViajeReparto.objects.create(
                    localidad_destino=localidad,
                    valor_viaje=Decimal(azar.randrange(60_000, 260_000)),
                ))

        for _ in range(40):
            destino = azar.choice(destinos)
            pagado = azar.random() < 0.65
            viaje = ViajeReparto.objects.create(
                fecha_viaje_reparto=hoy - timedelta(days=azar.randrange(1, 360)),
                empleado=azar.choice(empleados),
                vehiculo=azar.choice(vehiculos),
                destino=destino,
                gasto_combustible_viaje_reparto=azar.randrange(40_000, 190_000),
                costo_empleado=azar.randrange(30_000, 120_000),
                valor_viaje=destino.valor_viaje or Decimal(azar.randrange(60_000, 260_000)),
                activo=False,
                pagado=pagado,
                fecha_pago=timezone.now() - timedelta(days=azar.randrange(1, 60)) if pagado else None,
            )
            for localidad in azar.sample(LOCALIDADES, azar.randrange(1, 4)):
                DetalleViajeReparto.objects.create(
                    viaje_reparto=viaje, destinos_reparto=localidad,
                )
            if azar.random() < 0.5:
                GastoViajeReparto.objects.create(
                    viaje_reparto=viaje,
                    gasto=azar.choice([t[0] for t in GastoViajeReparto.TIPO_GASTOS]),
                    monto=azar.randrange(10_000, 90_000),
                )

    def _viajes_cereales(self, azar, hoy, empleados, vehiculos, clientes):
        dadoras = ["Acopio del Sur", "Cerealera La Pampa", "Granos Pico SA", ""]
        for _ in range(30):
            dadora = azar.choice(dadoras)
            pagado = azar.random() < 0.6
            viaje = ViajeCereal.objects.create(
                fecha_viaje_cereal=hoy - timedelta(days=azar.randrange(1, 360)),
                empleado=azar.choice(empleados),
                vehiculo=azar.choice(vehiculos),
                cliente=azar.choice(clientes) if azar.random() < 0.7 else None,
                tipo_cereal=azar.choice([c[0] for c in ViajeCereal.cereales]),
                codigo_trazabilidad_granos=f"CTG{azar.randrange(10_000_000, 99_999_999)}",
                numero_factura=f"0001-{azar.randrange(10_000, 99_999)}" if azar.random() < 0.6 else None,
                toneladas=Decimal(azar.randrange(18, 32)) + Decimal("0.50"),
                precio_tonelada=azar.randrange(28_000, 62_000),
                porcentaje_empleado=azar.choice([8, 10, 12, 15]),
                activo=False,
                pagado=pagado,
                fecha_pago=timezone.now() - timedelta(days=azar.randrange(1, 60)) if pagado else None,
                dadora_carga=dadora,
                dadora_tipo_cobro=azar.choice(["porcentaje", "tonelada", "efectivo"]) if dadora else "",
                dadora_valor=azar.randrange(5, 15) if dadora else 0,
            )
            for destino in azar.sample(LOCALIDADES, azar.randrange(1, 3)):
                DetalleViajeCereal.objects.create(viaje_cereal=viaje, destino=destino)
            if azar.random() < 0.6:
                GastoViajeCereal.objects.create(
                    viaje_cereal=viaje,
                    gasto=azar.choice([t[0] for t in GastoViajeCereal.TIPO_GASTOS]),
                    monto=azar.randrange(20_000, 150_000),
                )

    # -------------------------------------------------------------- auxiliares

    def _combustible(self, azar, hoy, empleados, vehiculos):
        estaciones = []
        for nombre in ["YPF Ruta 5", "Shell General Pico", "Axion Realico", "Puma Santa Rosa"]:
            estacion, _ = EstacionDeServicio.objects.get_or_create(nombre=nombre)
            estaciones.append(estacion)

        for _ in range(60):
            litros = Decimal(azar.randrange(80, 420))
            CargaCombustible.objects.create(
                estacion=azar.choice(estaciones),
                empleado=azar.choice(empleados),
                vehiculo=azar.choice(vehiculos),
                fecha=hoy - timedelta(days=azar.randrange(1, 300)),
                monto=(litros * Decimal(azar.randrange(1_150, 1_480))).quantize(Decimal("0.01")),
                litros=litros,
                pagada=azar.random() < 0.7,
                activa=True,
            )

    def _cheques(self, azar, hoy):
        empresas = []
        for nombre in ["MRM Acopio de Miel y Cera", "Del Sur Distribuciones", "Southern Honey Group"]:
            empresa, _ = Empresa.objects.get_or_create(nombre=nombre)
            empresas.append(empresa)

        bancos = []
        for nombre in ["Banco Nacion", "Banco Provincia", "Banco Galicia", "Banco Macro", "BBVA"]:
            banco, _ = Banco.objects.get_or_create(nombre=nombre)
            bancos.append(banco)

        cuentas = []
        for empresa in empresas:
            for banco in azar.sample(bancos, 2):
                cuentas.append(CuentaCorriente.objects.create(
                    empresa=empresa, banco=banco,
                    numero=f"{azar.randrange(1000, 9999)}-{azar.randrange(100000, 999999)}/{azar.randrange(1, 9)}",
                    activa=True,
                ))

        conceptos = [
            "Pago a proveedor de tambores", "Compra de cera estampada",
            "Anticipo de flete", "Pago de combustible mensual",
            "Compra de miel a granel", "Servicio de camion", "Insumos apicolas",
        ]
        for _ in range(40):
            emision = hoy - timedelta(days=azar.randrange(0, 200))
            # Reparto los cobros antes y despues de hoy: asi la pantalla muestra
            # cheques ya vencidos, otros al dia y otros a futuro
            cobro = emision + timedelta(days=azar.randrange(15, 220))
            Cheque.objects.create(
                cuenta_corriente=azar.choice(cuentas),
                numero=str(azar.randrange(10_000_000, 99_999_999)),
                fecha_emision=emision,
                fecha_cobro=cobro,
                concepto=azar.choice(conceptos),
                importe=Decimal(azar.randrange(150_000, 4_800_000)),
                cobrado=cobro < hoy and azar.random() < 0.8,
            )

    def _pagos_empleados(self, azar, hoy, empleados):
        for empleado in empleados:
            for mes in range(azar.randrange(3, 10)):
                PagosEmpleados.objects.create(
                    empleado=empleado,
                    fecha=hoy - timedelta(days=mes * 30 + azar.randrange(0, 5)),
                    monto=(empleado.sueldo or Decimal(800_000)) / Decimal(azar.choice([1, 2, 4])),
                    observaciones=azar.choice(["", "", "Adelanto", "Quincena", "Sueldo completo"]),
                    origen=PagosEmpleados.ORIGEN_MANUAL,
                )
