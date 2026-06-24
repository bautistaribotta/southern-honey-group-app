import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_detalleviajecereal_viajereparto_activo_viajecereal'),
    ]

    operations = [
        # El modelo DetalleViajeCereal habia quedado vacio (solo id). Lo elimino para
        # recrearlo con la estructura maestro-detalle (FK al viaje + destino).
        migrations.DeleteModel(
            name='DetalleViajeCereal',
        ),
        # tipo_cereal pasa a ser obligatorio (sin null/blank).
        migrations.AlterField(
            model_name='viajecereal',
            name='tipo_cereal',
            field=models.CharField(choices=[('Maiz', 'Maiz'), ('Soja', 'Soja'), ('Trigo', 'Trigo')], max_length=50),
        ),
        # El CTG pasa de entero a texto de 8 caracteres para preservar ceros a la izquierda.
        migrations.AlterField(
            model_name='viajecereal',
            name='codigo_trazabilidad_granos',
            field=models.CharField(max_length=8),
        ),
        migrations.CreateModel(
            name='DetalleViajeCereal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destino', models.CharField(max_length=30)),
                ('viaje_cereal', models.ForeignKey(db_column='id_viajecereal', on_delete=django.db.models.deletion.CASCADE, related_name='destinos', to='main.viajecereal')),
            ],
            options={
                'db_table': 'detalle_viaje_cereal',
            },
        ),
    ]
