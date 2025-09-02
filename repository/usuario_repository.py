import json
import os

class UsuarioRepositorio:
    Arquivo = "usuarios.json"

    @classmethod
    def carregar_usuarios(cls):
        try:
            if os.path.exists(cls.Arquivo):
                with open(cls.Arquivo, "r", encoding="utf-8") as arquivo:
                    return json.load(arquivo)
            else:
                return []
        except (IOError, json.JSONDecodeError):
            return []

    @classmethod
    def salvar_usuario(cls, usuario):
        usuarios = cls.carregar_usuarios()
        try:
            usuarios.append(usuario)
            with open(cls.Arquvio, "w", encoding="utf-8") as arquivo:
                json.dump(usuarios, arquivo, indent=4)
            return True
        except (IOError, TypeError):
            return False

    @classmethod
    def deletar_usuario_util(cls,id):
        usuarios = cls.carregar_usuarios()
        usuarios_filtrados = [usuario for usuario in usuarios if usuario.get("id") != id]
            
        if len(usuarios) == len(usuarios_filtrados):
            return False
            
        try:
            with open(cls.Arquivo, "w", encoding="utf-8") as arquivo:
                json.dump(usuarios_filtrados, arquivo, indent=4)
            return True
        except (IOError, TypeError):
                return False
        
    @classmethod
    def atualizar_usuario(cls, id_usuario, novos_dados):

        usuarios = cls.carregar_usuarios()
        usuario_encontrado = False
        for i, usuario in enumerate(usuarios):
            if str(usuario['id']) == str(id_usuario): 
                usuarios[i].update(novos_dados)
                usuario_encontrado = True
                break
            
        if not usuario_encontrado:
            return False 
            
        try:
            with open(cls.Arquivo, "w", encoding="utf-8") as f:
                json.dump(usuarios, f, indent=4)
            return True
        except (IOError, TypeError):
            return False
        
    @classmethod
    def buscar_por_id(cls, id):
        usuarios = cls.carregar_usuarios()
        for usuario in usuarios:
            if str(usuario.get("id")) == str(id):
                return usuario
        return None 
        
    @classmethod
    def buscar_por_email(cls, email):
        usuarios = cls.carregar_usuarios()
        for usuario in usuarios:
            if usuario.get("email") == email:
                return usuario
        return None 