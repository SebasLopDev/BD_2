# consultas.py
import io
import pandas as pd
import pymysql
from bd import obtener_conexion



def insertar_usuario_y_paciente(nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email, contrasena, id_rol):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            id_paciente = None
            id_medico = None

            if str(id_rol) == "1":
                sql_paciente = """
                    INSERT INTO paciente (nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_paciente, (nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email))
                id_paciente = cursor.lastrowid

            elif str(id_rol) == "2":
                sql_medico = """
                    INSERT INTO medico (nombre, apellido, email, estado)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_medico, (nombre, apellido, email, 'activo'))
                id_medico = cursor.lastrowid

            # ✨ Todo limpio, ordenado y exacto en minúsculas
            sql_usuario = """
                INSERT INTO usuario_sistema (nombre_user, contrasena_user, email_user, id_rol, id_paciente, id_medico)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (nombre, contrasena, email, id_rol, id_paciente, id_medico))

        conexion.commit()
    except Exception as e:
        print("Error en el registro:", e)
        raise e
    finally:
        conexion.close()

        
        
def obtener_usuario_paciente_por_dni(dni):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """ SELECT us.*, p.nombre, p.id_paciente AS paciente_id
                FROM Usuario_Sistema us
                JOIN Paciente p ON us.id_paciente = p.id_paciente
                WHERE p.dni = %s AND us.id_rol = 1 """

            cursor.execute(sql, (dni,))
            return cursor.fetchone()
    finally:
        conexion.close()
        
def obtener_usuario_medico_por_email(email):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT us.*, m.nombre, m.id_medico AS medico_id
                FROM Usuario_Sistema us
                JOIN Medico m ON us.id_medico = m.id_medico
                WHERE us.email_user = %s AND us.id_rol = 2
            """
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        conexion.close()

def obtener_citas_por_paciente(paciente_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT c.*, m.nombre AS nombre_medico, s.nombre AS nombre_sala
                FROM Cita c
                JOIN Medico m ON c.id_medico = m.id_medico
                LEFT JOIN Sala s ON c.id_sala = s.id_sala
                WHERE c.id_paciente = %s
            """
            cursor.execute(sql, (paciente_id,))
            return cursor.fetchall()
    finally:
        conexion.close()
        
def insertar_cita(fecha, hora, motivo, id_medico, id_paciente, id_sala):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Cita (fecha, hora, motivo, id_medico, id_paciente, id_sala)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, hora, motivo, id_medico, id_paciente, id_sala))
            conexion.commit()
    finally:
        conexion.close()

def obtener_cita_por_id(id_cita):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT c.*, me.id_especialidad
                FROM Cita c
                JOIN Medico_Especialidad me ON c.id_medico = me.id_medico
                WHERE c.id_cita = %s
            """
            cursor.execute(sql, (id_cita,))
            return cursor.fetchone()
    finally:
        conexion.close()

'''def obtener_cita_por_id(id_cita):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM Cita WHERE id_cita = %s"
            cursor.execute(sql, (id_cita,))
            return cursor.fetchone()
    finally:
        conexion.close()'''


def actualizar_cita(id_cita, fecha, hora, motivo, id_medico, id_sala=None):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = """
                UPDATE Cita
                SET fecha = %s, hora = %s, motivo = %s, id_medico = %s, id_sala = %s
                WHERE id_cita = %s
            """
            cursor.execute(sql, (fecha, hora, motivo, id_medico, id_sala, id_cita))
        conexion.commit()
    finally:
        conexion.close()


def eliminar_cita(id_cita):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = "DELETE FROM Cita WHERE id_cita = %s"
            cursor.execute(sql, (id_cita,))
        conexion.commit()
    finally:
        conexion.close()

def obtener_medicos_activos():
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM Medico WHERE estado = 'activo'"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_salas_disponibles():
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM Sala WHERE estado = 'disponible'"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conexion.close()
        
        
 #otras funciones
def obtener_especialidades():
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Especialidad")
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_especialidades_con_descripcion():
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT id_especialidad, nombre_espclidad, descripcion_espclidad FROM especialidad order by nombre_espclidad")
            return cursor.fetchall()
    finally:
        conexion.close()
        
def obtener_medicos_por_especialidad(id_especialidad):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT m.id_medico, m.nombre, m.apellido
                FROM Medico m
                JOIN Medico_Especialidad me ON m.id_medico = me.id_medico
                WHERE me.id_especialidad = %s
            """, (id_especialidad,))
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_turnos_medico(id_medico):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT dia_semana, hora_inicio, hora_fin
                FROM Turno_Medico
                WHERE id_medico = %s
            """, (id_medico,))
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_precio_por_especialidad(id_especialidad):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT precio_consulta FROM Especialidad WHERE id_especialidad = %s
            """, (id_especialidad,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
    finally:
        conexion.close()
        
'''def obtener_sala_disponible_para_medico(id_medico, fecha, hora):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT s.id_sala
                FROM Sala s
                WHERE s.estado = 'disponible'
                AND NOT EXISTS (
                    SELECT 1 FROM Cita c
                    WHERE c.id_sala = s.id_sala AND c.fecha = %s AND c.hora = %s
                )
                LIMIT 1
            """, (fecha, hora))
            resultado = cursor.fetchone()
            return resultado["id_sala"] if resultado else None
    finally:
        conexion.close()

''' 
def obtener_sala_disponible_para_medico(id_medico, fecha, hora):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT s.id_sala
                FROM Sala s
                WHERE s.estado = 'disponible'
                AND NOT EXISTS (
                    SELECT 1 FROM Cita c
                    WHERE c.id_sala = s.id_sala AND c.fecha = %s AND c.hora = %s
                )
                LIMIT 1
            """, (fecha, hora))
            resultado = cursor.fetchone()
            return resultado['id_sala'] if resultado else None
    finally:
        conexion.close()
              
def listar_doctores():
    conn = obtener_conexion()

    if not conn:
        return[ ]

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nombre, apellido, email FROM Medico WHERE estado='activo'")
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        print("Error al listar doctores:", e)
        return []
    finally:
        if conn:
            conn.close()    


#ADMIN
 
 # Obtener todos los pacientes (devolviendo lista de dicts)
def get_all_pacientes():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                  p.id_paciente,
                  p.nombre        AS nombre_paciente,
                  p.apellido      AS apellido_paciente,
                  p.dni,
                  p.fecha_nacimiento,
                  p.sexo,
                  p.telefono,
                  p.direccion,
                  p.email         AS email_paciente,
                  u.id_usuario,
                  u.nombre_user   AS nombre_usuario,
                  u.email_user    AS email_usuario
                FROM Paciente p
                LEFT JOIN Usuario_Sistema u
                  ON u.id_paciente = p.id_paciente
            """)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()


# Actualizar paciente y usuario asociado
def update_paciente(id_paciente, nombre, apellido, dni,
                    fecha_nacimiento, sexo, telefono,
                    direccion, email):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            # 1) Actualiza Paciente
            cursor.execute(
                """
                UPDATE Paciente
                   SET nombre = %s,
                       apellido = %s,
                       dni = %s,
                       fecha_nacimiento = %s,
                       sexo = %s,
                       telefono = %s,
                       direccion = %s,
                       email = %s
                 WHERE id_paciente = %s
                """,
                (nombre, apellido, dni, fecha_nacimiento,
                 sexo, telefono, direccion, email,
                 id_paciente)
            )
            # 2) Actualiza Usuario_Sistema (solo nombre_user y email_user)
            cursor.execute(
                """
                UPDATE Usuario_Sistema
                   SET nombre_user = %s,
                       email_user  = %s
                 WHERE id_paciente = %s
                """,
                (nombre, email, id_paciente)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error al actualizar paciente y usuario:", e)
        return False
    finally:
        conn.close()
# Eliminar paciente y usuario asociado
def eliminar_paciente(id_paciente):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Usuario_Sistema WHERE id_paciente = %s",
                (id_paciente,)
            )
            cursor.execute(
                "DELETE FROM Paciente WHERE id_paciente = %s",
                (id_paciente,)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error al eliminar paciente y usuario:", e)
        return False
    finally:
        conn.close()
        
def eliminar_paciente_completo(id_paciente):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            # 1. Obtener todas las citas del paciente
            cursor.execute("SELECT id_cita FROM Cita WHERE id_paciente = %s", (id_paciente,))
            citas = [row[0] for row in cursor.fetchall()]

            if citas:
                citas_str = ','.join(map(str, citas))  # para usar en IN (...)

                # 2. Eliminar relaciones que dependen de las citas
                cursor.execute(f"""
                    DELETE FROM Receta_Medicamento 
                    WHERE id_receta IN (
                        SELECT id_receta FROM Receta WHERE id_cita IN ({citas_str})
                    )
                """)

                cursor.execute(f"DELETE FROM Receta WHERE id_cita IN ({citas_str})")

                cursor.execute(f"""
                    DELETE FROM Tratamiento 
                    WHERE id_diagnostico IN (
                        SELECT id_diagnostico FROM Diagnostico WHERE id_cita IN ({citas_str})
                    )
                """)

                cursor.execute(f"DELETE FROM Diagnostico WHERE id_cita IN ({citas_str})")

                cursor.execute(f"DELETE FROM Examen_Medico WHERE id_cita IN ({citas_str})")
                cursor.execute(f"DELETE FROM Pago WHERE id_cita IN ({citas_str})")

                # 3. Eliminar las citas
                cursor.execute("DELETE FROM Cita WHERE id_paciente = %s", (id_paciente,))

            # 4. Eliminar facturas
            cursor.execute("DELETE FROM Factura WHERE id_paciente = %s", (id_paciente,))

            # 5. Eliminar usuario asociado
            cursor.execute("DELETE FROM Usuario_Sistema WHERE id_paciente = %s", (id_paciente,))

            # 6. Eliminar historial médico (si existiera)
            cursor.execute("SELECT id_historial_medico FROM Paciente WHERE id_paciente = %s", (id_paciente,))
            fila = cursor.fetchone()
            if fila and fila[0]:
                id_historial = fila[0]
                cursor.execute("DELETE FROM Historial_Medico WHERE id_historial_medico = %s", (id_historial,))

            # 7. Eliminar paciente
            cursor.execute("DELETE FROM Paciente WHERE id_paciente = %s", (id_paciente,))

        conn.commit()
        print("Paciente y relaciones eliminados correctamente.")
        return True

    except Exception as e:
        conn.rollback()
        print("Error al eliminar completamente al paciente:", e)
        return False

    finally:
        conn.close()
        

def insertar_paciente_con_usuario(
    nombre, apellido, dni, fecha_nacimiento,
    sexo, telefono, direccion, email,
    nombre_user, contrasena_user,
    id_rol=1  # 1 = PACIENTE
):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            # Insertar Paciente
            cursor.execute(
                """
                INSERT INTO Paciente (
                  nombre, apellido, dni, fecha_nacimiento,
                  sexo, telefono, direccion, email
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (nombre, apellido, dni, fecha_nacimiento,
                 sexo, telefono, direccion, email)
            )
            id_paciente = cursor.lastrowid
            # Insertar Usuario_Sistema
            cursor.execute(
                """
                INSERT INTO Usuario_Sistema (
                  nombre_user, contrasena_user, email_user,
                  id_rol, id_paciente
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (nombre_user, contrasena_user, email, id_rol, id_paciente)
            )
        conn.commit()
        return id_paciente
    except Exception as e:
        conn.rollback()
        print("Error al insertar paciente+usuario:", e)
        return None
    finally:
        conn.close()
# Listar doctores y datos de usuario asociado
def get_all_doctores():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                  m.id_medico,
                  m.nombre        AS nombre_medico,
                  m.apellido      AS apellido_medico,
                  m.email         AS email_medico,
                  m.estado,
                  u.id_usuario,
                  u.nombre_user   AS nombre_usuario,
                  u.email_user    AS email_usuario
                FROM Medico m
                LEFT JOIN Usuario_Sistema u ON u.id_medico = m.id_medico
            """)
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in rows]
    finally:
        conn.close()

# Insertar doctor + usuario en transacciÃ³n
def insertar_doctor_con_usuario(
    nombre, apellido, email, estado,
    nombre_user, contrasena_user,
    id_rol=2  # 2 = MEDICO
):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            # 1) Insertar en Medico
            cursor.execute(
                """
                INSERT INTO Medico (nombre, apellido, email, estado)
                VALUES (%s, %s, %s, %s)
                """,
                (nombre, apellido, email, estado)
            )
            id_medico = cursor.lastrowid
            # 2) Insertar en Usuario_Sistema
            cursor.execute(
                """
                INSERT INTO Usuario_Sistema (
                  nombre_user, contrasena_user, email_user,
                  id_rol, id_medico
                ) VALUES (%s, %s, %s, %s, %s)
                """,
                (nombre_user, contrasena_user, email, id_rol, id_medico)
            )
        conn.commit()
        return id_medico
    except Exception as e:
        conn.rollback()
        print("Error al insertar doctor+usuario:", e)
        return None
    finally:
        conn.close()

# Actualizar doctor + usuario asociado
def update_doctor(id_medico, nombre, apellido, email, estado):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            # Actualizar Medico
            cursor.execute(
                """
                UPDATE Medico
                   SET nombre   = %s,
                       apellido = %s,
                       email    = %s,
                       estado   = %s
                 WHERE id_medico = %s
                """,
                (nombre, apellido, email, estado, id_medico)
            )
            # Actualizar Usuario_Sistema
            cursor.execute(
                """
                UPDATE Usuario_Sistema
                   SET nombre_user = %s,
                       email_user  = %s
                 WHERE id_medico = %s
                """,
                (nombre, email, id_medico)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error al actualizar doctor y usuario:", e)
        return False
    finally:
        conn.close()

# Eliminar doctor + usuario asociado
def eliminar_doctor(id_medico):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Usuario_Sistema WHERE id_medico = %s",
                (id_medico,)
            )
            cursor.execute(
                "DELETE FROM Medico WHERE id_medico = %s",
                (id_medico,)
            )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error al eliminar doctor y usuario:", e)
        return False
    finally:
        conn.close()


#--------------
def get_pacientes_dataframe(desde=None, hasta=None, sexo=None, texto_busqueda=None):
    sql = """
      SELECT
        p.fecha_nacimiento         AS fecha_nacimiento,
        p.id_paciente,
        p.nombre,
        p.apellido,
        p.dni,
        p.sexo,
        p.email                   AS email_paciente,
        u.nombre_user             AS usuario_sistema
      FROM Paciente p
      LEFT JOIN Usuario_Sistema u ON u.id_paciente = p.id_paciente
      WHERE 1=1
    """
    params = []
    if desde:
        sql += " AND p.fecha_nacimiento >= %s"
        params.append(desde)
    if hasta:
        sql += " AND p.fecha_nacimiento <= %s"
        params.append(hasta)
    if sexo:
        sql += " AND p.sexo = %s"
        params.append(sexo)
    if texto_busqueda:
        sql += " AND (p.nombre LIKE %s OR p.apellido LIKE %s OR p.dni LIKE %s)"
        like = f"%{texto_busqueda}%"
        params.extend([like, like, like])

    conn = obtener_conexion()
    try:
        df = pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()
    return df       
        

'''def obtener_doctores_por_especialidad(id_especialidad):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT m.id_medico, m.nombre, m.apellido, m.email, e.nombre_espclidad
                FROM Medico m
                JOIN Medico_Especialidad me ON m.id_medico = me.id_medico
                JOIN Especialidad e ON me.id_especialidad = e.id_especialidad
                WHERE me.id_especialidad = %s
            """
            cursor.execute(sql, (id_especialidad,))
            return cursor.fetchall()
    finally:
        conexion.close()'''        
            
   
'''def insertar_paciente(nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    sql = """
        INSERT INTO Paciente (
            nombre, apellido, dni, fecha_nacimiento,
            sexo, telefono, direccion, email
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    valores = (nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email)

    try:
        cursor.execute(sql, valores)
        conexion.commit()
        print("Paciente insertado correctamente.")
    except pymysql.MySQLError as e:
        print("Error al insertar paciente:", e)
    finally:
        cursor.close()
        conexion.close()'''
    