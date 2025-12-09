# SmartConnect API - Sistema de Control de Acceso RFID

**Versión:** 1.0.0  
**Estado:** ✅ En producción  
**URL Producción:** `http://52.22.98.94:8000/`  
**Documentación API:** `http://52.22.98.94:8000/api/docs/`  
**Desarrolladores:** Matias Vega, Alma Vargas  
**Asignatura:** Programación Back End - INACAP  
**Última actualización:** Enero 2024

## 📋 Tabla de Contenidos
- [Características](#-características-principales)
- [Tecnologías](#-tecnologías-utilizadas)
- [Instalación](#-instalación-y-configuración)
- [Estructura](#-estructura-del-proyecto)
- [API Reference](#-api-reference)
- [Modelos](#-modelos-de-datos)
- [Base de Datos](#-base-de-datos)
- [Despliegue](#-despliegue-en-aws)
- [Testing](#-testing)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuidores](#-contribuidores)

## 🚀 Características Principales

### ✅ CRUD Completo
- **Usuarios:** Gestión con roles (Administrador/Operador)
- **Departamentos:** Torres y números
- **Sensores:** RFID (Tarjetas/Llaveros)
- **Eventos:** Logs de acceso en tiempo real

### 🔐 Autenticación y Seguridad
- JWT (JSON Web Tokens) con refresh tokens
- Permisos por roles (Administrador/Operador)
- Validaciones avanzadas de datos
- Base de datos MySQL encriptada
- CORS configurado para producción

### ⚡ Funcionalidades Especiales
- Validación RFID en tiempo real
- Control manual de barrera desde API
- Historial de acceso con filtros
- Dashboard administrativo
- Exportación de logs

## 🛠️ Tecnologías Utilizadas

### Backend
- **Framework:** Django 4.2.7
- **API:** Django REST Framework 3.14.0
- **Lenguaje:** Python 3.9
- **Base de Datos:** MySQL 10.5
- **Autenticación:** Simple JWT 5.3.0

### Servidor
- **Servidor Web:** Apache 2.4
- **WSGI:** Gunicorn 21.2.0
- **Hosting:** AWS EC2 (Ubuntu 20.04 LTS)
- **IP Pública:** 52.22.98.94

### Frontend
- **Admin:** Django Admin Panel
- **API Browser:** DRF Browsable API
- **Documentación:** Swagger UI

## 📦 Instalación y Configuración

### Prerrequisitos
```bash
# Versiones requeridas
Python 3.9+
MySQL 10.5+
pip 22.0+
```

### 1. Clonar y Configurar
```bash
# Clonar repositorio
git clone [url-repositorio]
cd django

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Base de Datos
```bash
# Acceder a MySQL
mysql -u root -p

# Crear base de datos
CREATE DATABASE diva_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Crear usuario
CREATE USER 'smartconnect_user'@'localhost' IDENTIFIED BY 'tu_password_seguro';
GRANT ALL PRIVILEGES ON diva_db.* TO 'smartconnect_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Configurar Variables de Entorno
```bash
# Crear archivo .env en la raíz del proyecto
cp .env.example .env
# Editar con tus valores
nano .env
```

**Contenido de .env:**
```env
DEBUG=False
SECRET_KEY=tu_secreto_django_aqui
DB_NAME=diva_db
DB_USER=smartconnect_user
DB_PASSWORD=tu_password_seguro
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=52.22.98.94,localhost,127.0.0.1
```

### 4. Migraciones y Usuario Inicial
```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# Usuario: admin@smartconnect.com
# Contraseña: Admin1234

# Cargar datos iniciales (opcional)
python manage.py loaddata initial_data.json

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
django/
├── api/                    # Aplicación principal
│   ├── views.py           (785 líneas - lógica completa)
│   ├── urls.py            # Rutas API
│   ├── models.py          # Modelos ORM
│   ├── serializers.py     # Serializadores
│   ├── routers.py         # Enrutadores API
│   ├── admin.py           # Configuración admin
│   ├── tests.py           # Tests unitarios
│   └── migrations/        # Migraciones de base de datos
├── smartconnect/          # Configuración proyecto
│   ├── settings.py        # Configuración principal
│   ├── urls.py            # URLs globales
│   ├── wsgi.py           # Configuración WSGI
│   └── asgi.py           # Configuración ASGI
├── manage.py              # CLI Django
├── requirements.txt       # Dependencias Python
├── .env.example          # Plantilla variables entorno
└── README.md             # Este archivo
```

## 📡 API Reference

### Autenticación

#### Obtener Token JWT
```http
POST /api/token/
Content-Type: application/json

{
    "username": "admin@smartconnect.com",
    "password": "Admin1234"
}
```

**Response:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "tu_refresh_token"
}
```

### Endpoints Públicos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/info/` | Información de la API |
| `POST` | `/api/validar-acceso/` | Validar acceso RFID |
| `GET` | `/api/docs/` | Documentación Swagger |

### Endpoints Protegidos (Requieren JWT)

#### Usuarios
```http
GET    /api/usuarios/         # Listar usuarios
POST   /api/usuarios/         # Crear usuario
GET    /api/usuarios/{id}/    # Detalle usuario
PUT    /api/usuarios/{id}/    # Actualizar usuario
DELETE /api/usuarios/{id}/    # Eliminar usuario
```

#### Departamentos
```http
GET    /api/departamentos/    # Listar departamentos
POST   /api/departamentos/    # Crear departamento
```

#### Sensores
```http
GET    /api/sensores/         # Listar sensores
POST   /api/sensores/         # Crear sensor
PATCH  /api/sensores/{id}/    # Actualizar estado
```

#### Eventos
```http
GET    /api/eventos-acceso/   # Historial de accesos
GET    /api/eventos-acceso/{id}/ # Detalle evento
```

#### Control de Barrera
```http
POST   /api/control-barrera/  # Control manual
```

### Ejemplos de Uso

#### 1. Listar Usuarios (con autenticación)
```bash
curl -H "Authorization: Bearer tu_token_jwt" \
  http://52.22.98.94:8000/api/usuarios/
```

#### 2. Validar Acceso RFID
```bash
curl -X POST http://52.22.98.94:8000/api/validar-acceso/ \
  -H "Content-Type: application/json" \
  -d '{"codigo_sensor":"43FEF4F5"}'
```

**Response exitosa:**
```json
{
    "status": "success",
    "access_granted": true,
    "user": {
        "id": 1,
        "nombres": "Juan Pérez",
        "email": "juan@email.com"
    },
    "department": "Torre A - 401",
    "sensor_type": "Tarjeta",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🗄️ Modelos de Datos

### Diagrama de Relaciones
```
Usuario (1) ──── (1) Sensor
    │
    └─── (1) Departamento
    │
    └─── (*) EventoAcceso
```

### Esquemas Principales

#### Usuario
```python
class Usuario(models.Model):
    nombres = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rol = models.CharField(choices=[('ADMINISTRADOR', 'Administrador'), ('Operador', 'Operador')])
    estado = models.CharField(choices=ESTADOS_USUARIO)
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True)
    sensor = models.OneToOneField('Sensor', on_delete=models.SET_NULL, null=True, blank=True)
```

#### Sensor
```python
class Sensor(models.Model):
    codigo_sensor = models.CharField(max_length=100, unique=True)  # UID/MAC
    tipo = models.CharField(choices=[('Tarjeta', 'Tarjeta'), ('Llavero', 'Llavero')])
    estado = models.CharField(choices=ESTADOS_SENSOR)
    usuario = models.OneToOneField(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
```

#### EventoAcceso
```python
class EventoAcceso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    acceso_permitido = models.BooleanField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    mensaje = models.TextField()
```

## 📊 Base de Datos

### Script de Creación (MySQL)
```sql
-- Crear base de datos
CREATE DATABASE diva_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Tabla usuarios
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombres VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    rol ENUM('ADMINISTRADOR','Operador') DEFAULT 'Operador',
    estado ENUM('ACTIVO','INACTIVO','BLOQUEADO','ELIMINADO') DEFAULT 'ACTIVO',
    departamento_id INT NULL,
    sensor_id INT UNIQUE NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id),
    FOREIGN KEY (sensor_id) REFERENCES sensores(id)
);

-- Tabla sensores
CREATE TABLE sensores (
    id_sensor INT PRIMARY KEY AUTO_INCREMENT,
    codigo_sensor VARCHAR(100) UNIQUE NOT NULL,
    tipo ENUM('Tarjeta','Llavero') NOT NULL,
    estado ENUM('ACTIVO','INACTIVO','BLOQUEADO') DEFAULT 'ACTIVO',
    usuario_id INT UNIQUE NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla eventos_acceso
CREATE TABLE eventos_acceso (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    sensor_id INT NOT NULL,
    acceso_permitido BOOLEAN NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mensaje TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (sensor_id) REFERENCES sensores(id),
    INDEX idx_fecha_hora (fecha_hora),
    INDEX idx_usuario (usuario_id)
);
```

### Índices Optimizados
- `idx_fecha_hora` en eventos_acceso para búsquedas rápidas
- `idx_usuario` para filtrado por usuario
- Claves únicas en email y codigo_sensor

## 🚀 Despliegue en AWS

### Especificaciones del Servidor
- **Servicio:** AWS EC2 t2.micro
- **OS:** Ubuntu 20.04 LTS
- **RAM:** 1 GB
- **Storage:** 8 GB SSD
- **IP Pública:** 52.22.98.94
- **Puertos:** 80 (HTTP), 443 (HTTPS), 8000 (API)

### Configuración Paso a Paso

#### 1. Conectar al servidor
```bash
ssh -i tu-key.pem ubuntu@52.22.98.94
```

#### 2. Instalar dependencias
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y herramientas
sudo apt install python3-pip python3-venv mysql-server apache2 libapache2-mod-wsgi-py3 -y

# Instalar dependencias de MySQL
sudo apt install libmysqlclient-dev pkg-config -y
```

#### 3. Configurar MySQL
```bash
# Seguridad MySQL
sudo mysql_secure_installation

# Crear base de datos y usuario
sudo mysql -u root -p
# Ejecutar script SQL anterior
```

#### 4. Configurar Apache
```apache
# /etc/apache2/sites-available/smartconnect.conf
<VirtualHost *:80>
    ServerName 52.22.98.94
    ServerAdmin webmaster@localhost
    
    # Directorio estático
    Alias /static /var/www/html/django/staticfiles
    <Directory /var/www/html/django/staticfiles>
        Require all granted
    </Directory>
    
    # Configuración WSGI
    WSGIDaemonProcess smartconnect python-path=/var/www/html/django python-home=/var/www/html/django/venv
    WSGIProcessGroup smartconnect
    WSGIScriptAlias / /var/www/html/django/smartconnect/wsgi.py
    
    <Directory /var/www/html/django/smartconnect>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

#### 5. Habilitar sitio
```bash
sudo a2ensite smartconnect.conf
sudo a2dissite 000-default.conf
sudo systemctl reload apache2
```

#### 6. Configurar permisos
```bash
sudo chown -R www-data:www-data /var/www/html/django
sudo chmod -R 755 /var/www/html/django
```

#### 7. Configurar Gunicorn (opcional)
```bash
# Instalar gunicorn
pip install gunicorn

# Crear servicio systemd
sudo nano /etc/systemd/system/gunicorn.service
```

**Contenido de gunicorn.service:**
```ini
[Unit]
Description=gunicorn daemon for SmartConnect
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/html/django
ExecStart=/var/www/html/django/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/html/django/smartconnect.sock smartconnect.wsgi:application

[Install]
WantedBy=multi-user.target
```

## 🧪 Testing

### Tests Unitarios
```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test api.tests.UserTests
python manage.py test api.tests.SensorTests
python manage.py test api.tests.AccessTests
```

### Tests de API con curl
```bash
# Test autenticación
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@test.com","password":"test123"}'

# Test validación RFID
curl -X POST http://localhost:8000/api/validar-acceso/ \
  -H "Content-Type: application/json" \
  -d '{"codigo_sensor":"TEST123"}'
```

### Cobertura de Tests
```bash
# Instalar coverage
pip install coverage

# Ejecutar con coverage
coverage run manage.py test
coverage report
coverage html  # Generar reporte HTML
```

## 🔍 Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. Error de conexión a MySQL
```bash
# Verificar servicio MySQL
sudo systemctl status mysql

# Revisar credenciales en settings.py
# Verificar permisos de usuario:
mysql -u root -p
GRANT ALL PRIVILEGES ON diva_db.* TO 'smartconnect_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2. Error 403 Forbidden en API
```bash
# Verificar token JWT
curl -H "Authorization: Bearer TU_TOKEN" http://localhost:8000/api/usuarios/

# Obtener nuevo token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -d 'refresh=TU_REFRESH_TOKEN'
```

#### 3. Error 500 Internal Server Error
```bash
# Revisar logs de Apache
sudo tail -f /var/log/apache2/error.log

# Revisar logs de aplicación
sudo journalctl -u apache2 -f
```

#### 4. Problemas con migraciones
```bash
# Resetear migraciones
python manage.py migrate --fake api zero
python manage.py makemigrations api
python manage.py migrate api
```

### Monitoreo y Logs
```bash
# Ver logs en tiempo real
sudo tail -f /var/log/apache2/access.log
sudo tail -f /var/log/apache2/error.log

# Ver uso de memoria
free -h
top

# Ver espacio en disco
df -h
```

## 👥 Contribuidores

### Desarrolladores Principales
- **Matias Vega** 
  
- **Alma Vargas**



## 📝 Changelog

### v1.0.0 (Enero 2024)
- ✅ CRUD completo de usuarios, departamentos y sensores
- ✅ Sistema de autenticación JWT con roles
- ✅ Validación RFID en tiempo real
- ✅ Historial de eventos de acceso
- ✅ Control manual de barrera
- ✅ Despliegue en AWS EC2
- ✅ Documentación completa API
- ✅ Tests unitarios básicos



## 📄 Licencia

Este proyecto fue desarrollado con fines académicos para el curso de Programación Back End de INACAP.

**Nota:** Este software no está listo para uso en producción crítica. Se recomienda revisión de seguridad antes de implementar en entornos reales.

---

**✨ Proyecto completamente funcional y desplegado en AWS**  
*Sistema de Control de Acceso RFID SmartConnect*  
Última actualización: Enero 2024
