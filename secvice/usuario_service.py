from model.usuario import Usuario
from repository.usuario_repository import UsuarioRepository
import bcrypt

class UsuarioService:
    @staticmethod
    def cadastrar(dados):
        usuario = Usuario(**dados)
    
    @staticmethod
    def autenticar(email, senha):
        usuario = UsuarioRepository.buscar_por_email(email)
        if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
            return usuario
        
    @staticmethod
    def atualizar(id_usuario, novos_dados):
        return UsuarioRepository.atualizar_usuario(id_usuario, novos_dados)
    
    @staticmethod
    def deletar(id_usuario):
        return UsuarioRepository.deletar_usuario_util(id_usuario)
    
    @staticmethod
    def listar():
        return UsuarioRepository.carregar_usuarios()