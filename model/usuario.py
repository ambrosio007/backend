import uuid
import bcrypt

class Usuario:
    # Adicionado 'perfil=None' ao construtor para evitar o NameError
    def __init__(self, nome, email, cpf, idade, senha, perfil="user", id=None):
        
        self.id = id or str(uuid.uuid4())
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.idade = idade
        
        # ⚠️ REMOVIDA A CRIPTOGRAFIA DA SENHA DAQUI. O Service irá fazer isso.
        self.senha = senha 
        
        # Atribuído o valor, usando 'user' como padrão se não for fornecido
        self.perfil = perfil 

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "cpf": self.cpf,
            "idade": self.idade,
            "senha": self.senha,
            "perfil": self.perfil
        }