from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_viajereparto_empleado_costo_viajereparto_valor_viaje'),
    ]

    operations = [
        migrations.RenameField(
            model_name='viajereparto',
            old_name='empleado_costo',
            new_name='costo_empleado',
        ),
    ]
