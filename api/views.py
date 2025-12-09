from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import mysql.connector
from django.http import JsonResponse
from datetime import datetime

# Configuración de MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Matias123456',
    'database': 'diva_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

# SISTEMA DE PERMISOS
def es_administrador(request):
    """Verificar si el usuario autenticado es administrador"""
    try:
        # Verificar el token JWT y obtener el usuario
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False
            
        # Para una implementación real:
        # 1. Decodificar el token JWT
        # 2. Obtener el user_id del token  
        # 3. Consultar la base de datos para verificar el rol
        # 4. Retornar True si el rol es 'ADMINISTRADOR'
        
        return True  # Temporal - cambiar por verificación real
        
    except Exception as e:
        print(f"Error verificando administrador: {e}")
        return False

# MANEJO DE ERRORES 404
def handler404(request, exception):
    return JsonResponse({
        "error": "Endpoint no encontrado",
        "codigo": "endpoint_no_existe",
        "mensaje": "La ruta solicitada no existe en la API",
        "endpoint_sugerido": "/api/info/ para información de la API"
    }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    info = {
        "autor": ["Matias Vega", "Alma Vargas"],
        "asignatura": "Programación Back End", 
        "proyecto": "SmartConnect API",
        "descripcion": "Sistema de control de acceso con sensores RFID",
        "version": "1.0",
        "fecha": "2025-11-29"
    }
    return Response(info)

# CRUD COMPLETO PARA DEPARTAMENTOS
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def departamentos_list(request):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM DEPARTAMENTOS")
            departamentos = cursor.fetchall()
            
            return Response({
                "status": "success",
                "count": len(departamentos),
                "data": departamentos
            })
        
        elif request.method == 'POST':
            # VERIFICAR PERMISOS (solo admin puede crear)
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden crear departamentos"
                }, status=status.HTTP_403_FORBIDDEN)
            
            numero = request.data.get('numero')
            torre = request.data.get('torre')
            
            # VALIDACIONES
            errors = []
            
            if not numero:
                errors.append({
                    "campo": "numero",
                    "codigo": "numero_requerido",
                    "mensaje": "El número de departamento es requerido"
                })
            
            if not torre:
                errors.append({
                    "campo": "torre",
                    "codigo": "torre_requerida", 
                    "mensaje": "La torre es requerida"
                })
            
            if errors:
                return Response({
                    "error": "Validación fallida",
                    "codigo": "validacion_error",
                    "errores": errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Insertar en la base de datos
            cursor.execute(
                "INSERT INTO DEPARTAMENTOS (numero, torre) VALUES (%s, %s)",
                (numero, torre)
            )
            conn.commit()
            
            nuevo_id = cursor.lastrowid
            
            # Obtener el departamento creado
            cursor.execute("SELECT * FROM DEPARTAMENTOS WHERE id_departamento = %s", (nuevo_id,))
            nuevo_departamento = cursor.fetchone()
            
            return Response({
                "status": "success",
                "mensaje": "Departamento creado exitosamente",
                "data": nuevo_departamento
            }, status=status.HTTP_201_CREATED)
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Ocurrió un error inesperado"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def departamento_detail(request, pk):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if not str(pk).isdigit():
            return Response({
                "error": "ID inválido",
                "codigo": "id_invalido",
                "mensaje": "El ID debe ser un número válido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pk = int(pk)
        
        if request.method == 'GET':
            cursor.execute("SELECT * FROM DEPARTAMENTOS WHERE id_departamento = %s", (pk,))
            departamento = cursor.fetchone()
            
            if not departamento:
                return Response({
                    "error": "Recurso no encontrado",
                    "codigo": "departamento_no_existe", 
                    "mensaje": f"El departamento con ID {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
                
            return Response({
                "status": "success",
                "data": departamento
            })
        
        elif request.method == 'PUT':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden actualizar departamentos"
                }, status=status.HTTP_403_FORBIDDEN)
            
            cursor.execute("SELECT * FROM DEPARTAMENTOS WHERE id_departamento = %s", (pk,))
            if not cursor.fetchone():
                return Response({
                    "error": "Recurso no encontrado",
                    "codigo": "departamento_no_existe",
                    "mensaje": f"No se puede actualizar - departamento {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
            
            numero = request.data.get('numero')
            torre = request.data.get('torre')
            
            cursor.execute(
                "UPDATE DEPARTAMENTOS SET numero = %s, torre = %s WHERE id_departamento = %s",
                (numero, torre, pk)
            )
            conn.commit()
                
            return Response({
                "status": "success", 
                "mensaje": f"Departamento {pk} actualizado exitosamente"
            })
        
        elif request.method == 'DELETE':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado", 
                    "mensaje": "Solo los administradores pueden eliminar departamentos"
                }, status=status.HTTP_403_FORBIDDEN)
            
            cursor.execute("SELECT * FROM DEPARTAMENTOS WHERE id_departamento = %s", (pk,))
            if not cursor.fetchone():
                return Response({
                    "error": "Recurso no encontrado",
                    "codigo": "departamento_no_existe",
                    "mensaje": f"No se puede eliminar - departamento {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
                
            cursor.execute("DELETE FROM DEPARTAMENTOS WHERE id_departamento = %s", (pk,))
            conn.commit()
            
            return Response({
                "status": "success",
                "mensaje": f"Departamento {pk} eliminado exitosamente"
            })
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Ocurrió un error inesperado"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

# CRUD COMPLETO PARA USUARIOS
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def usuarios_list(request):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'GET':
            cursor.execute("""
                SELECT u.id, u.nombres, u.apellido, u.email, u.rol, u.estado, 
                       d.numero, d.torre,
                       CONCAT(d.torre, ' - ', d.numero) as departamento
                FROM usuarios u 
                LEFT JOIN DEPARTAMENTOS d ON u.id_departamento = d.id_departamento
                WHERE u.estado != 'ELIMINADO'
            """)
            usuarios = cursor.fetchall()
            
            return Response({
                "status": "success",
                "count": len(usuarios),
                "data": usuarios
            })
        
        elif request.method == 'POST':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden crear usuarios"
                }, status=status.HTTP_403_FORBIDDEN)
            
            nombres = request.data.get('nombres')
            apellido = request.data.get('apellido')
            email = request.data.get('email')
            rol = request.data.get('rol', 'Operador')
            id_departamento = request.data.get('id_departamento')
            clave = request.data.get('clave', 'Temp1234')

            # VALIDACIONES DETALLADAS
            errors = []
            
            if not nombres:
                errors.append({
                    "campo": "nombres",
                    "codigo": "nombres_requerido", 
                    "mensaje": "Los nombres son requeridos"
                })
            elif len(nombres) < 2:
                errors.append({
                    "campo": "nombres",
                    "codigo": "nombres_invalidos",
                    "mensaje": "Los nombres deben tener al menos 2 caracteres"
                })
                
            if not apellido:
                errors.append({
                    "campo": "apellido",
                    "codigo": "apellido_requerido",
                    "mensaje": "El apellido es requerido"
                })
                
            if not email:
                errors.append({
                    "campo": "email", 
                    "codigo": "email_requerido",
                    "mensaje": "El email es requerido"
                })
            elif '@' not in email:
                errors.append({
                    "campo": "email",
                    "codigo": "email_invalido",
                    "mensaje": "El formato del email es inválido"
                })
            
            if rol not in ['ADMINISTRADOR', 'Operador']:
                errors.append({
                    "campo": "rol",
                    "codigo": "rol_invalido",
                    "mensaje": "El rol debe ser ADMINISTRADOR o Operador"
                })
            
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                errors.append({
                    "campo": "email",
                    "codigo": "email_duplicado",
                    "mensaje": "El email ya está registrado"
                })
            
            if errors:
                return Response({
                    "error": "Validación fallida",
                    "codigo": "validacion_error",
                    "errores": errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Insertar en la base de datos
            cursor.execute(
                """INSERT INTO usuarios 
                (nombres, apellido, email, clave, rol, id_departamento, estado) 
                VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO')""",
                (nombres, apellido, email, clave, rol, id_departamento)
            )
            conn.commit()
            
            nuevo_id = cursor.lastrowid
            
            # Obtener el usuario creado
            cursor.execute("""
                SELECT u.id, u.nombres, u.apellido, u.email, u.rol, u.estado, 
                       d.numero, d.torre,
                       CONCAT(d.torre, ' - ', d.numero) as departamento
                FROM usuarios u 
                LEFT JOIN DEPARTAMENTOS d ON u.id_departamento = d.id_departamento
                WHERE u.id = %s
            """, (nuevo_id,))
            
            nuevo_usuario = cursor.fetchone()
            
            return Response({
                "status": "success",
                "mensaje": "Usuario creado exitosamente",
                "data": nuevo_usuario
            }, status=status.HTTP_201_CREATED)
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Ocurrió un error inesperado"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def usuario_detail(request, pk):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if not str(pk).isdigit():
            return Response({
                "error": "ID inválido",
                "codigo": "id_invalido",
                "mensaje": "El ID debe ser un número válido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pk = int(pk)
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT u.id, u.nombres, u.apellido, u.email, u.rol, u.estado, 
                       d.numero, d.torre,
                       CONCAT(d.torre, ' - ', d.numero) as departamento
                FROM usuarios u 
                LEFT JOIN DEPARTAMENTOS d ON u.id_departamento = d.id_departamento
                WHERE u.id = %s AND u.estado != 'ELIMINADO'
            """, (pk,))
            
            usuario = cursor.fetchone()
            
            if not usuario:
                return Response({
                    "error": "Usuario no encontrado",
                    "codigo": "usuario_no_existe",
                    "mensaje": f"El usuario con ID {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
                
            return Response({
                "status": "success",
                "data": usuario
            })
        
        elif request.method == 'PUT':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden actualizar usuarios"
                }, status=status.HTTP_403_FORBIDDEN)
            
            cursor.execute("SELECT id FROM usuarios WHERE id = %s AND estado != 'ELIMINADO'", (pk,))
            if not cursor.fetchone():
                return Response({
                    "error": "Usuario no encontrado",
                    "codigo": "usuario_no_existe",
                    "mensaje": f"No se puede actualizar - usuario {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
            
            nombres = request.data.get('nombres')
            apellido = request.data.get('apellido')
            email = request.data.get('email')
            rol = request.data.get('rol')
            id_departamento = request.data.get('id_departamento')
            
            cursor.execute(
                """UPDATE usuarios SET 
                nombres = %s, apellido = %s, email = %s, rol = %s, id_departamento = %s 
                WHERE id = %s""",
                (nombres, apellido, email, rol, id_departamento, pk)
            )
            conn.commit()
                
            return Response({
                "status": "success",
                "mensaje": f"Usuario {pk} actualizado exitosamente"
            })
        
        elif request.method == 'DELETE':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden eliminar usuarios"
                }, status=status.HTTP_403_FORBIDDEN)
            
            cursor.execute("SELECT id FROM usuarios WHERE id = %s AND estado != 'ELIMINADO'", (pk,))
            if not cursor.fetchone():
                return Response({
                    "error": "Usuario no encontrado", 
                    "codigo": "usuario_no_existe",
                    "mensaje": f"No se puede eliminar - usuario {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
                
            # Soft delete - marcar como eliminado
            cursor.execute("UPDATE usuarios SET estado = 'ELIMINADO' WHERE id = %s", (pk,))
            conn.commit()
            
            return Response({
                "status": "success",
                "mensaje": f"Usuario {pk} eliminado exitosamente"
            })
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error", 
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Ocurrió un error inesperado"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

# CRUD COMPLETO PARA SENSORES
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sensores_list(request):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'GET':
            cursor.execute("""
                SELECT s.id_sensor, s.codigo_sensor, s.tipo, s.estado, s.fecha_alta,
                       u.nombres, u.apellido,
                       d.numero, d.torre,
                       CONCAT(u.nombres, ' ', u.apellido) as usuario,
                       CONCAT(d.torre, ' - ', d.numero) as departamento
                FROM SENSORES s
                LEFT JOIN usuarios u ON s.id_usuario = u.id
                LEFT JOIN DEPARTAMENTOS d ON s.id_departamento = d.id_departamento
            """)
            sensores = cursor.fetchall()
            
            return Response({
                "status": "success",
                "count": len(sensores),
                "data": sensores
            })
    
        elif request.method == 'POST':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden crear sensores"
                }, status=status.HTTP_403_FORBIDDEN)
            
            codigo_sensor = request.data.get('codigo_sensor')
            tipo = request.data.get('tipo')
            estado = request.data.get('estado', 'ACTIVO')
            id_usuario = request.data.get('id_usuario')
            id_departamento = request.data.get('id_departamento')
            
            # VALIDACIONES DETALLADAS
            errors = []
            
            if not codigo_sensor:
                errors.append({
                    "campo": "codigo_sensor",
                    "codigo": "codigo_requerido",
                    "mensaje": "El código del sensor es requerido"
                })
            elif len(codigo_sensor) < 4:
                errors.append({
                    "campo": "codigo_sensor",
                    "codigo": "codigo_invalido",
                    "mensaje": "El código del sensor debe tener al menos 4 caracteres",
                    "longitud_minima": 4
                })
            
            if not tipo:
                errors.append({
                    "campo": "tipo",
                    "codigo": "tipo_requerido", 
                    "mensaje": "El tipo es requerido"
                })
            elif tipo not in ['Tarjeta', 'Llavero']:
                errors.append({
                    "campo": "tipo",
                    "codigo": "tipo_invalido",
                    "mensaje": "El tipo debe ser 'Tarjeta' o 'Llavero'",
                    "valores_permitidos": ["Tarjeta", "Llavero"]
                })
            
            if estado not in ['ACTIVO', 'INACTIVO', 'BLOQUEADO']:
                errors.append({
                    "campo": "estado",
                    "codigo": "estado_invalido",
                    "mensaje": "El estado debe ser ACTIVO, INACTIVO o BLOQUEADO",
                    "valores_permitidos": ["ACTIVO", "INACTIVO", "BLOQUEADO"]
                })
            
            # Verificar si el código del sensor ya existe (MAC única)
            cursor.execute("SELECT id_sensor FROM SENSORES WHERE codigo_sensor = %s", (codigo_sensor,))
            if cursor.fetchone():
                errors.append({
                    "campo": "codigo_sensor",
                    "codigo": "codigo_duplicado",
                    "mensaje": "El código del sensor ya está registrado"
                })
            
            if errors:
                return Response({
                    "error": "Validación fallida",
                    "codigo": "validacion_error",
                    "errores": errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Insertar en la base de datos
            cursor.execute(
                """INSERT INTO SENSORES 
                (codigo_sensor, tipo, estado, id_usuario, id_departamento) 
                VALUES (%s, %s, %s, %s, %s)""",
                (codigo_sensor, tipo, estado, id_usuario, id_departamento)
            )
            conn.commit()
            
            nuevo_id = cursor.lastrowid
            
            # Obtener el sensor creado
            cursor.execute("""
                SELECT s.id_sensor, s.codigo_sensor, s.tipo, s.estado, s.fecha_alta,
                       u.nombres, u.apellido,
                       d.numero, d.torre,
                       CONCAT(u.nombres, ' ', u.apellido) as usuario,
                       CONCAT(d.torre, ' - ', d.numero) as departamento
                FROM SENSORES s
                LEFT JOIN usuarios u ON s.id_usuario = u.id
                LEFT JOIN DEPARTAMENTOS d ON s.id_departamento = d.id_departamento
                WHERE s.id_sensor = %s
            """, (nuevo_id,))
            
            nuevo_sensor = cursor.fetchone()
            
            return Response({
                "status": "success",
                "mensaje": "Sensor creado exitosamente",
                "data": nuevo_sensor
            }, status=status.HTTP_201_CREATED)
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Ocurrió un error inesperado"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def sensor_detail(request, pk):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if not str(pk).isdigit():
            return Response({
                "error": "ID inválido",
                "codigo": "id_invalido",
                "mensaje": "El ID debe ser un número válido"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pk = int(pk)
        
        if request.method == 'GET':
            cursor.execute("""
                SELECT s.id_sensor, s.codigo_sensor, s.tipo, s.estado, s.fecha_alta,
                       u.nombres, u.apellido,
                       d.numero, d.torre,
                       CONCAT(u.nombres, ' ', u.apellido) as usuario,
                       CONCAT(d.torre, ' - ', d.numero) as departamento
                FROM SENSORES s
                LEFT JOIN usuarios u ON s.id_usuario = u.id
                LEFT JOIN DEPARTAMENTOS d ON s.id_departamento = d.id_departamento
                WHERE s.id_sensor = %s
            """, (pk,))
            
            sensor = cursor.fetchone()
            
            if not sensor:
                return Response({
                    "error": "Sensor no encontrado",
                    "codigo": "sensor_no_existe",
                    "mensaje": f"El sensor con ID {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
                
            return Response({
                "status": "success",
                "data": sensor
            })
        
        elif request.method == 'PUT':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden actualizar sensores"
                }, status=status.HTTP_403_FORBIDDEN)
            
            cursor.execute("SELECT id_sensor FROM SENSORES WHERE id_sensor = %s", (pk,))
            if not cursor.fetchone():
                return Response({
                    "error": "Sensor no encontrado",
                    "codigo": "sensor_no_existe",
                    "mensaje": f"No se puede actualizar - sensor {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
            
            codigo_sensor = request.data.get('codigo_sensor')
            tipo = request.data.get('tipo')
            estado = request.data.get('estado')
            id_usuario = request.data.get('id_usuario')
            id_departamento = request.data.get('id_departamento')
            
            cursor.execute(
                """UPDATE SENSORES SET 
                codigo_sensor = %s, tipo = %s, estado = %s, id_usuario = %s, id_departamento = %s
                WHERE id_sensor = %s""",
                (codigo_sensor, tipo, estado, id_usuario, id_departamento, pk)
            )
            conn.commit()
                
            return Response({
                "status": "success",
                "mensaje": f"Sensor {pk} actualizado exitosamente"
            })
        
        elif request.method == 'DELETE':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden eliminar sensores"
                }, status=status.HTTP_403_FORBIDDEN)
            
            cursor.execute("SELECT id_sensor FROM SENSORES WHERE id_sensor = %s", (pk,))
            if not cursor.fetchone():
                return Response({
                    "error": "Sensor no encontrado",
                    "codigo": "sensor_no_existe", 
                    "mensaje": f"No se puede eliminar - sensor {pk} no existe"
                }, status=status.HTTP_404_NOT_FOUND)
                
            cursor.execute("DELETE FROM SENSORES WHERE id_sensor = %s", (pk,))
            conn.commit()
            
            return Response({
                "status": "success",
                "mensaje": f"Sensor {pk} eliminado exitosamente"
            })
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Ocurrió un error inesperado"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

# SISTEMA RFID COMPLETO - VALIDACIÓN DE ACCESO
@api_view(['POST'])
@permission_classes([AllowAny])
def validar_acceso_rfid(request):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        codigo_sensor = request.data.get('codigo_sensor')
        
        if not codigo_sensor:
            return Response({
                "error": "Validación fallida",
                "codigo": "codigo_sensor_requerido",
                "mensaje": "El código del sensor es requerido para validar acceso"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar el sensor en la base de datos
        cursor.execute("""
            SELECT s.*, u.nombres, u.apellido, u.rol, u.estado as usuario_estado,
                   d.numero, d.torre
            FROM SENSORES s
            LEFT JOIN usuarios u ON s.id_usuario = u.id
            LEFT JOIN DEPARTAMENTOS d ON s.id_departamento = d.id_departamento
            WHERE s.codigo_sensor = %s
        """, (codigo_sensor,))
        
        sensor = cursor.fetchone()
        
        if not sensor:
            # Registrar evento de acceso denegado (sensor no encontrado)
            cursor.execute("""
                INSERT INTO EVENTOS_ACCESO 
                (id_sensor, tipo_evento, resultado) 
                VALUES (NULL, 'ACCESO_DESCONOCIDO', 'DENEGADO')
            """)
            conn.commit()
            
            return Response({
                "status": "error", 
                "acceso": "DENEGADO",
                "mensaje": "Sensor no registrado en el sistema",
                "codigo": "sensor_no_encontrado"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validar estado del sensor
        if sensor['estado'] != 'ACTIVO':
            cursor.execute("""
                INSERT INTO EVENTOS_ACCESO 
                (id_sensor, id_usuario, id_departamento, tipo_evento, resultado) 
                VALUES (%s, %s, %s, 'ACCESO_RECHAZADO', 'DENEGADO')
            """, (sensor['id_sensor'], sensor['id_usuario'], sensor['id_departamento']))
            conn.commit()
            
            return Response({
                "status": "error",
                "acceso": "DENEGADO", 
                "mensaje": f"Sensor {sensor['estado'].lower()}",
                "codigo": f"sensor_{sensor['estado'].lower()}"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validar estado del usuario
        if sensor['usuario_estado'] != 'ACTIVO':
            cursor.execute("""
                INSERT INTO EVENTOS_ACCESO 
                (id_sensor, id_usuario, id_departamento, tipo_evento, resultado) 
                VALUES (%s, %s, %s, 'ACCESO_RECHAZADO', 'DENEGADO')
            """, (sensor['id_sensor'], sensor['id_usuario'], sensor['id_departamento']))
            conn.commit()
            
            return Response({
                "status": "error",
                "acceso": "DENEGADO",
                "mensaje": f"Usuario {sensor['usuario_estado'].lower()}",
                "codigo": f"usuario_{sensor['usuario_estado'].lower()}"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # ACCESO PERMITIDO - Registrar evento exitoso
        cursor.execute("""
            INSERT INTO EVENTOS_ACCESO 
            (id_sensor, id_usuario, id_departamento, tipo_evento, resultado) 
            VALUES (%s, %s, %s, 'ACCESO_VALIDO', 'PERMITIDO')
        """, (sensor['id_sensor'], sensor['id_usuario'], sensor['id_departamento']))
        conn.commit()
        
        return Response({
            "status": "success",
            "acceso": "PERMITIDO",
            "mensaje": "Acceso autorizado",
            "usuario": f"{sensor['nombres']} {sensor['apellido']}",
            "departamento": f"{sensor['torre']} - {sensor['numero']}",
            "rol": sensor['rol'],
            "sensor_tipo": sensor['tipo']
        })
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Error al validar acceso"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

# SISTEMA DE CONTROL DE BARRERA
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def control_barrera(request):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        if request.method == 'GET':
            # Obtener estado actual de la barrera
            cursor.execute("SELECT * FROM ESTADO_SISTEMA WHERE id = 1")
            estado = cursor.fetchone()
            
            return Response({
                "status": "success",
                "data": estado
            })
        
        elif request.method == 'POST':
            # VERIFICAR PERMISOS
            if not tiene_permiso_escritura(request):
                return Response({
                    "error": "Permisos insuficientes",
                    "codigo": "permiso_denegado",
                    "mensaje": "Solo los administradores pueden controlar la barrera"
                }, status=status.HTTP_403_FORBIDDEN)
            
            accion = request.data.get('accion')  # 'abrir' o 'cerrar'
            
            if accion not in ['abrir', 'cerrar']:
                return Response({
                    "error": "Acción inválida",
                    "codigo": "accion_invalida",
                    "mensaje": "La acción debe ser 'abrir' o 'cerrar'"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            nuevo_estado = 'Abierta' if accion == 'abrir' else 'Cerrada'
            
            # Actualizar estado de la barrera
            cursor.execute(
                "UPDATE ESTADO_SISTEMA SET estado_barrera = %s, ultimo_cambio = NOW() WHERE id = 1",
                (nuevo_estado,)
            )
            conn.commit()
            
            # Registrar evento manual
            cursor.execute("""
                INSERT INTO EVENTOS_ACCESO 
                (id_usuario, tipo_evento, resultado) 
                VALUES (1, 'APERTURA_MANUAL', 'PERMITIDO')
            """)
            conn.commit()
            
            return Response({
                "status": "success",
                "mensaje": f"Barrera {accion}da exitosamente",
                "estado_actual": nuevo_estado
            })
            
    except mysql.connector.Error as e:
        conn.rollback()
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        conn.rollback()
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": "Error al controlar barrera"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()

# ENDPOINT PARA EVENTOS DE ACCESO (LOGS)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eventos_acceso(request):
    conn = get_db_connection()
    if not conn:
        return Response({
            "error": "Error de base de datos",
            "codigo": "db_error",
            "mensaje": "No se pudo conectar a la base de datos"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        limit = request.GET.get('limit', 50)
        
        cursor.execute("""
            SELECT e.*, s.codigo_sensor, u.nombres, u.apellido, 
                   d.numero, d.torre
            FROM EVENTOS_ACCESO e
            LEFT JOIN SENSORES s ON e.id_sensor = s.id_sensor
            LEFT JOIN usuarios u ON e.id_usuario = u.id
            LEFT JOIN DEPARTAMENTOS d ON e.id_departamento = d.id_departamento
            ORDER BY e.fecha_hora DESC
            LIMIT %s
        """, (int(limit),))
        
        eventos = cursor.fetchall()
        
        return Response({
            "status": "success",
            "count": len(eventos),
            "data": eventos
        })
            
    except Exception as e:
        return Response({
            "error": "Error interno del servidor",
            "codigo": "error_interno",
            "mensaje": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()
