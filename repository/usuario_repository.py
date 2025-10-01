import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="lafj2001@",   # sua senha aqui
        database="crud_db"
    )

class UsuarioRepository:

    @staticmethod
    def carregar_usuarios():
        """Retorna todos os usuários do banco."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return usuarios

    @staticmethod
    def salvar_usuario(usuario):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (id, nome, cpf, email, idade, senha, perfil)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                usuario["id"],
                usuario["nome"],
                usuario["cpf"],
                usuario["email"],
                usuario["idade"],
                usuario["senha"],
                usuario.get("perfil", "user")  # padrão "user"
            ))
            conn.commit()
            return True
        except Exception as e:
            print("Erro ao salvar usuário:", e)
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return usuario

    @staticmethod
    def deletar_usuario_util(id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()
        return deleted > 0

    @staticmethod
    def atualizar_usuario(id_usuario, novos_dados):
        campos = []
        valores = []

        for campo in ["nome", "cpf", "email", "idade", "senha", "perfil"]:
            if campo in novos_dados:
                campos.append(f"{campo} = %s")
                valores.append(novos_dados[campo])

        if not campos:  
            return False

        sql = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = %s"
        valores.append(id_usuario)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, tuple(valores))
        conn.commit()
        updated = cursor.rowcount
        cursor.close()
        conn.close()
        return updated > 0
