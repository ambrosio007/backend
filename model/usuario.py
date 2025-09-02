import uuid
import bcrypt

class Usuario:
    def __init__(self, nome, email, cpf, idade, senha, id = None):
        self.id = id or str(uuid.uuid4())
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.idade = idade
        self.senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
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