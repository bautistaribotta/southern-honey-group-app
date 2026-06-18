# Southern Honey Group - Staff Portal

## Prueba la demo: https://bautistaribotta.pythonanywhere.com/
<u>Datos de ingreso al portal</u> <br>
Usuario: usuario <br>
Clave: User1234!

Portal interno de gestión administrativa desarrollado para Southern Honey Group. Centraliza el control de stock, clientes, operaciones comerciales y viajes de distribución.

---

## Módulos

* **Dashboard:** Cotización actualizada del dólar oficial y paralelo mediante consumo de DolarAPI. Precio del kilo de miel configurable.
* **Inventario:** CRUD de productos con categorías, control de stock y baja lógica. Registra cantidad vendida y comprada por producto.
* **Clientes:** Registro de clientes con datos de contacto, domicilio y datos de facturación (CUIT, condición de facturación). Baja lógica.
* **Operaciones:** Compras y ventas vinculadas a un cliente y opcionalmente a un viaje. Estado de pago calculado dinámicamente (Debe / Pago Parcial / Pagada / Cancelada). Soporta pagos parciales. Generación de remitos.
* **Deudores:** Vista filtrable con operaciones impagas o con saldo pendiente, ordenables por monto y antigüedad.
* **Viajes:** Registro de viajes de distribución con chofer, vehículo, destinos múltiples e inicio de caja. Gastos asociados por tipo (combustible, peaje, comida, etc.) con cálculo de caja final. Operaciones vinculables al viaje. Baja lógica.
* **Flota:** Administración de choferes y vehículos con conteo de viajes activos por entidad.

---

## Tecnologías

**Backend**

* Python 3.10+
* Django 6.0.2 — lógica de negocio, ORM, enrutamiento, autenticación y CSRF
* MySQL — motor de base de datos relacional

**Librerías Python**

* `requests` — peticiones HTTP hacia APIs externas

**Integraciones externas**

* DolarAPI (`/v1/dolares/oficial` y `blue`) — cotización del dólar en tiempo real

**Frontend**

* HTML 5
* CSS 3
* JavaScript Vanilla — modales, slide-overs, carrito de productos, filtros y validaciones de formularios

---

## Arquitectura

El proyecto sigue el patrón MVT de Django con una capa de servicios adicional:

* **Models:** Relaciones con `PROTECT` en claves foráneas críticas y `UniqueConstraint` para garantizar integridad de datos. Baja lógica mediante campo `activo` en las entidades principales. Totales de operaciones calculados como `@property` sobre los detalles y pagos asociados, con soporte de anotaciones ORM (`con_totales()`) para evitar el problema N+1 en listados.
* **Services (`services.py`):** Aísla las transacciones de base de datos y el consumo de APIs externas, manteniendo las vistas enfocadas únicamente en el flujo HTTP.

---

## Instalación y Configuración Local

Asegúrese de tener instalado Python 3.10+ y un servidor MySQL ejecutándose localmente.

**1. Clonar el repositorio**

```bash
git clone <https://github.com/bautistaribotta/southern_honey_group.git>
cd southern_honey_group

```

**2. Crear y activar el entorno virtual**

```bash
python -m venv venv

# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

```

**3. Instalar las dependencias**

```bash
pip install -r requirements.txt

```

**4. Configurar las variables de entorno**
Cree un archivo `.env` en la raíz del proyecto (al mismo nivel que `manage.py`) con las siguientes credenciales para conectar su base de datos local y asegurar el proyecto:

```env
SECRET_KEY=ingrese_su_secret_key_aqui
DB_NAME=nombre_de_su_base_de_datos
DB_USER=su_usuario_mysql
DB_PASSWORD=su_contraseña_mysql
DB_HOST=localhost
DB_PORT=3306

```

**5. Ejecutar migraciones**

```bash
python manage.py makemigrations
python manage.py migrate

```

**6. Crear un superusuario (opcional pero recomendado)**

```bash
python manage.py createsuperuser

```

**7. Iniciar el servidor de desarrollo**

```bash
python manage.py runserver

```

El software estará disponible de forma local ingresando a `http://127.0.0.1:8000/`.

---

## Datos personales

**Bautista Ribotta**
Desarrollador Full Stack a cargo del ciclo de vida completo del software: analisis de requerimientos, diseño UI/UX, modelado de la base de datos y programación del backend y frontend.
