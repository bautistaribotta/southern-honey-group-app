from django.db import migrations


"""
Alta de "Cera Borra de Operculo" como articulo de cotizacion: comparte el
comportamiento de Cera Operculo y Cera Recupero (precio desde el tablero de
cotizaciones, solo lectura en el inventario) y nace mostrandose en inicio.

El nombre va escrito y no importado de ARTICULOS_COTIZACION porque una
migracion de datos es una foto de este momento: si manana cambia la tupla del
modelo, cambia hacia adelante y no reescribe lo que ya se aplico.
"""
ARTICULO = "Cera Borra de Operculo"


def crear(apps, schema_editor):
    ProductoPorKg = apps.get_model("main", "ProductoPorKg")
    # get_or_create y no create: la base de la demo puede tenerlo cargado a mano
    ProductoPorKg.objects.get_or_create(
        articulo=ARTICULO,
        defaults={
            "categoria": "Cera",
            # monto arranca en 1 (el default del modelo) para que se note que
            # todavia no tiene cotizacion cargada, igual que un articulo nuevo
            "monto": 1,
            "cantidad": 0,
            "activo": True,
            "mostrar_en_inicio": True,
        },
    )


def borrar(apps, schema_editor):
    """
    Solo lo borro si nunca se uso: si ya tiene detalles de operacion asociados,
    la FK es PROTECT y borrarlo se llevaria puesto el historial. En ese caso lo
    dejo, que es la baja logica que usa el resto del sistema.
    """
    ProductoPorKg = apps.get_model("main", "ProductoPorKg")
    DetalleOperacion = apps.get_model("main", "DetalleOperacion")

    articulo = ProductoPorKg.objects.filter(articulo=ARTICULO).first()
    if articulo is None:
        return

    if DetalleOperacion.objects.filter(cotizacion=articulo).exists():
        ProductoPorKg.objects.filter(pk=articulo.pk).update(activo=False, mostrar_en_inicio=False)
    else:
        articulo.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0088_marcar_productos_de_inicio"),
    ]

    operations = [
        migrations.RunPython(crear, borrar),
    ]
