from django.db import models

class Departamento(models.Model):
    id_departamento = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=50)
    torre = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'DEPARTAMENTOS'
        
    def __str__(self):
        return f"{self.torre} - {self.numero}"

class Usuario(models.Model):
    ROL_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('Operador', 'Operador'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
        ('ELIMINADO', 'Eliminado'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    clave = models.CharField(max_length=100)
    codigo_recuperacion = models.CharField(max_length=5, null=True, blank=True)
    codigo_expira = models.DateTimeField(null=True, blank=True)
    # CORREGIDO: Usar db_column para especificar el nombre exacto
    id_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_departamento')
    rol = models.CharField(max_length=50, choices=ROL_CHOICES, default='Operador')
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='ACTIVO')
    
    class Meta:
        db_table = 'usuarios'
        
    def __str__(self):
        return f"{self.nombres} {self.apellido}"

class Sensor(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('BLOQUEADO', 'Bloqueado'),
    ]
    
    TIPO_CHOICES = [
        ('Tarjeta', 'Tarjeta'),
        ('Llavero', 'Llavero'),
    ]
    
    id_sensor = models.AutoField(primary_key=True)
    codigo_sensor = models.CharField(max_length=100, unique=True)
    # CORREGIDO: Especificar db_column
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='ACTIVO')
    # CORREGIDO: Especificar db_column
    id_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_departamento')
    fecha_alta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'SENSORES'
        
    def __str__(self):
        return f"Sensor {self.codigo_sensor}"

class EventoAcceso(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('ACCESO_VALIDO', 'Acceso Válido'),
        ('ACCESO_RECHAZADO', 'Acceso Rechazado'),
        ('ACCESO_DESCONOCIDO', 'Acceso Desconocido'),
        ('APERTURA_MANUAL', 'Apertura Manual'),
        ('CIERRE_MANUAL', 'Cierre Manual'),
        ('APERTURA_MANUAL (APP)', 'Apertura Manual (APP)'),
        ('CIERRE_MANUAL (APP)', 'Cierre Manual (APP)'),
    ]
    
    RESULTADO_CHOICES = [
        ('PERMITIDO', 'Permitido'),
        ('DENEGADO', 'Denegado'),
        ('0', 'Sin resultado'),
    ]
    
    id_evento = models.AutoField(primary_key=True)
    # CORREGIDO: Especificar db_column
    id_sensor = models.ForeignKey(Sensor, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_sensor')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_usuario')
    id_departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_departamento')
    tipo_evento = models.CharField(max_length=100, choices=TIPO_EVENTO_CHOICES)
    resultado = models.CharField(max_length=50, choices=RESULTADO_CHOICES)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'EVENTOS_ACCESO'
        
    def __str__(self):
        return f"Evento {self.id_evento} - {self.tipo_evento}"

class EstadoSistema(models.Model):
    id = models.AutoField(primary_key=True)
    estado_barrera = models.CharField(max_length=50, default='Cerrada')
    ultimo_cambio = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ESTADO_SISTEMA'
        
    def __str__(self):
        return f"Barrera: {self.estado_barrera}"
