import pymysql # type: ignore
import pymysql.cursors # type: ignore

class Connexio(object):
    def conecta(self):
        self.db = pymysql.connect(
            host="192.168.193.133",  
            port=3306,
            user="joancortes",
            password="43481462P",
            db="gpt4",
            charset="utf8mb4",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.db.cursor()

    def desconecta(self):
        self.db.close()

    def cargaUsuari(self, username, password):
        sql = (" SELECT * FROM usuarisclase WHERE username = %s and password = %s ") 
        self.cursor.execute(sql, (username, password))
        ResQuery = self.cursor.fetchall()
        return ResQuery
    
    def cargaHashedPassword(self, username):
        sql = "SELECT password FROM usuarisclase WHERE username LIKE %s "
        self.cursor.execute(sql, (username))
        ResQuery = self.cursor.fetchone()
        return ResQuery['password']

    def cargaLlistaAmics(self):
        sql = "SELECT * FROM usuarisclase"
        self.cursor.execute(sql)
        ResQuery = self.cursor.fetchall()
        return ResQuery

    # /grupos
    def sacaGruposDelUser(self, username):
        sql = """SELECT gdu.grupo_id 
                FROM grupos_de_usuarios gdu
                JOIN usuarisclase u ON gdu.usuario_id = u.id
                WHERE u.username = %s" """
        self.cursor.execute(sql, (username))
        ResQuery = self.cursor.fetchall()
        return ResQuery

    def creaGrupos(self, nom, descripcio, creador_id):

        sql = """INSERT INTO grupos(nom, descripcio, creador_id)
                VALUES (%s, %s, %s, %s)"""
        self.cursor.execute(sql, (nom, descripcio, creador_id)) #creador el que crida a l'api
        ResQuery = self.cursor.fetchall()
        return ResQuery

    def cargaMensajesAmigos(self):
        sql = """SELECT emisor_id, receptor_id, contenido, fecha_envio, estado FROM  mensajes_usuarios mu 
                JOIN usuarisclase u ON mu.id = u.id"""
        self.cursor.execute(sql)
        ResQuery = self.cursor.fetchall()
        return ResQuery

    def cargaMensajesAmigo(self, username):
        sql = ("SELECT emisor_id, receptor_id, contenido, fecha_envio, estado "
                "FROM mensajes_usuarios mu "
                "JOIN usuarisclase u ON mu.id = u.id "
                "WHERE u.username LIKE %s;")

        self.cursor.execute(sql, (username))
        ResQuery = self.cursor.fetchall()
        return ResQuery

    def añadirAlGrupo(self, username):
        sql = (
                "INSERT INTO grupos_de_usuarios (grupo_id, usuario_id) "
                "VALUES (%s, (SELECT id FROM usuarisclase WHERE username = %s))"
            )

        self.cursor.execute(sql, (username))
        ResQuery = self.cursor.fetchall()
        return ResQuery

    # carga los mensajes de todos los grupos en los que este un usuario en concreto.
    def cargaMensajeGrupo(self, username):
        sql = """
        SELECT 
     	    g.nom AS nombre_grupo, 
            mg.contenido, 
            mg.fecha_envio,
            u_emisor.username AS emisor_username  -- Nombre del usuario que envió el mensaje
        FROM 
            mensajes_grupos mg 
        INNER JOIN 
            grupos g ON mg.id = g.id
        INNER JOIN 
            grupos_de_usuarios gdu ON gdu.grupo_id = g.id
        INNER JOIN 
            usuarisclase u ON u.id = gdu.usuario_id
        INNER JOIN 
            usuarisclase u_emisor ON u_emisor.id = mg.emisor_id  -- Unir con la tabla de usuarios para obtener el emisor
        WHERE 
            u.username = "%s" 
        ORDER BY 
            g.nom ASC, mg.fecha_envio ASC;
        """
        self.cursor.execute(sql, (username,))  # Asegúrate de pasar el parámetro como una tupla
        ResQuery = self.cursor.fetchall()
        return ResQuery

    def enviarMensajeGrupo(self, emisor, contenido, fecha, grup):
        sql = """ 
        INSERT INTO mensajes_grupo (emisor_id, contenido, fecha_envio) 
        SELECT %s, %s, %s 
        FROM grupos 
        WHERE grupos.nom = %s;
        """
        try:
            self.cursor.execute(sql, (emisor, contenido, fecha, grup))
            self.db.commit()  # Confirmar la transacción
            return True 
        except Exception as e:
            print(f"Error al enviar el mensaje: {e}")
            self.db.rollback()  # Revertir la transacción en caso de error
            return False

    def enviaMensajesAmigos(self, emisor_id, receptor_id, contenido):
        sql = """ INSERT INTO mensajes_usuarios (emisor_id, receptor_id, contenido) 
        VALUES (%s, %s, %s); """
        self.cursor.execute(sql, (emisor_id, receptor_id, contenido))
        ResQuery = self.cursor.fetchall()
        return ResQuery

    def transforma_Username_a_ID(self,username):
        sql = """ SELECT id FROM usuarisclase WHERE username = %s """

        self.cursor.execute(sql, (username))
        ResQuery = self.cursor.fetchone()
        return ResQuery

    def modificaEstatMissatgeUsuarios(self, estat, missatge_id):
        sql = """ UPDATE mensajes_usuarios 
                SET estado = "'%s'"
                WHERE id LIKE '%s' """
        self.cursor.execute(sql, (estat, missatge_id))
        ResQuery = self.cursor.fetchone()
        return ResQuery

    def check_missatge (self,missatge_id,missatge_grup) :
        sql = "SELECT * FROM missatges WHERE missatge_id = %s and missatge_grup = %s"
        self.cursor.execute(sql, (missatge_id, missatge_grup))
        update_sql = "UPDATE missatges SET estat = 'vist' WHERE missatge_id = %s and missatge_grup = %s"
        self.cursor.execute(update_sql, (missatge_id, missatge_grup))
        ResQuery = self.cursor.fetchall()
        return ResQuery
