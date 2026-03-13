# Southern Honey Group - Staff Portal

Portal interno de gestión administrativa, control de stock, clientes y facturación desarrollado para la empresa Southern Honey Group. Este sistema centraliza las operaciones diarias, digitalizando el seguimiento de inventarios y la información financiera en tiempo real.

El proyecto es desarrollado, diseñado y mantenido de manera independiente, abarcando tanto la arquitectura del backend como el diseño de la interfaz de usuario.

---

## Características Principales

* **Panel de Control (Dashboard):** Visualización en tiempo real de variables económicas clave mediante la integración de APIs externas y rutinas de extracción de datos.
* **Gestión de Inventario:** Sistema CRUD para la administración de productos (miel, alimento, cera, madera, medicamentos, etc.). 
* **Administración de Clientes:** Registro detallado de clientes con soporte para datos de facturación
* **Gestión de Operaciones:** Seguimiento de deudores, remitos e historial de compras utilizando un diseño de base de datos relacional para vincular clientes, operaciones y detalle de productos.
* **Autenticación y Seguridad:** Sistema de login seguro con control de sesiones, implementando decoradores de Django para restringir el acceso únicamente al personal autorizado.

---

## Librerías, Integraciones y Tecnologías Utilizadas

**Backend y Lógica de Negocio**

* **Python 3.10+**
* **Django 6.0.2:** Framework principal para la lógica de negocio, ORM, enrutamiento y seguridad (manejo de CSRF y autenticación).
* **MySQL:** Motor de base de datos relacional.

**Librerías de Terceros (Python)**

* **Requests:** Utilizada para realizar peticiones HTTP seguras hacia servicios externos y APIs.
* **BeautifulSoup4 (bs4):** Implementada para el análisis y parseo de documentos HTML en las rutinas de web scraping.

**Integraciones Externas**

* **DolarAPI:** Consumo de API RESTful (`https://dolarapi.com/v1/dolares/oficial` y `blue`) para obtener la cotización actualizada del dólar oficial y paralelo.
* **Web Scraping (Infomiel):** Rutina automatizada sobre el sitio `infomiel.com` para la extracción en tiempo real del valor del kilogramo de miel clara y oscura, filtrando el contenido del DOM para obtener únicamente los valores numéricos limpios.

**Frontend**

* **HTML5 & CSS3:** Diseño estructurado y modular empleando variables nativas de CSS.
* **HTMX:** Para interacciones dinámicas con el DOM sin necesidad de recargar la página completa ni escribir JavaScript complejo.
* **JavaScript Vanilla:** Manejo de componentes interactivos de la UI, como los modales de tipo Slide-Over y lógica de formularios.

---

## Arquitectura del Proyecto

El proyecto sigue el patrón de diseño MVT (Model-View-Template) propio de Django, pero incorpora una capa adicional de abstracción en su arquitectura:

* **Models:** Definen la estructura estricta de la base de datos con restricciones como `PROTECT` en llaves foráneas y `UniqueConstraint` para garantizar la coherencia de las transacciones comerciales.
* **Services (`services.py`):** Toda la lógica externa (consumo de APIs, rutinas de Web Scraping con BeautifulSoup4) y las transacciones de creación, edición o eliminación lógica de la base de datos están aisladas en este módulo, manteniendo las vistas (`views.py`) limpias y enfocadas únicamente en el manejo del flujo de las peticiones HTTP.

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

El portal estará disponible de forma local ingresando a `http://127.0.0.1:8000/`.

---

## Datos personales

**Bautista Ribotta**
Desarrollador Full Stack a cargo del ciclo de vida completo del software: analisis de requerimientos, diseño UI/UX, modelado de la base de datos y programación integral del backend y frontend.
