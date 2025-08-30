from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import uuid
import bcrypt

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

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

# ------------ Routes ------------ #

@app.route("/")
def home():
    return render_template("form.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    nome = request.form.get("nome")
    email = request.form.get("email")
    idade = request.form.get("idade")
    cpf = request.form.get("cpf")
    senha = request.form.get("senha")
    
    usuario = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "email": email,
        "cpf": cpf,
        "idade": idade,
        "senha": senha
    }
    
    status = UsuarioRepositorio.salvar_usuario(usuario)
    
    if status:
        return f"Usuário '{usuario['nome']}' cadastrado com sucesso!"
    else:
        return "Não foi possível cadastrar o usuário!"

@app.route("/usuarios/json")
def usuarios_json():
    usuarios = UsuarioRepositorio.carregar_usuarios()
    return jsonify(usuarios)

@app.route("/listar-usuarios")
def listar_usuarios():
    usuarios = UsuarioRepositorio.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    sucesso = UsuarioRepositorio.deletar_usuario_util(id)
    if sucesso:
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    else:
        return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404

@app.route("/editar-usuario/<id>")
def editar_usuario(id):
    usuarios = UsuarioRepositorio.carregar_usuarios()
    usuario = next((u for u in usuarios if str(u['id']) == str(id)), None)
    if usuario:
        return render_template("editar_usuario.html", usuario=usuario)
    else:
        return "Usuário não encontrado!", 404

@app.route("/usuarios/<id>", methods=["PUT"])
def atualizar_usuario_api(id):
    novos_dados = request.get_json()
    if not novos_dados:
        return jsonify({"message": "Dados inválidos!"}), 400
    
    sucesso = UsuarioRepositorio.atualizar_usuario(id, novos_dados)
    if sucesso:
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    else:
        return jsonify({"message": "Usuário não encontrado ou erro na atualização!"}), 404
    
# ----------------- Login / Logout ----------------- #

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioRepositorio.buscar_por_email(email)
    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
        session['usuario_id'] = usuario['id']
        session['perfil'] = usuario['perfil']
        return f"Login bem-sucedido! Bem-vindo, {usuario['nome']}."
    return "Email ou senha incorretos!", 401

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------- Rotas Protegidas ----------------- #

@app.route("/usuarios/json")
def buscar_usuarios_json():
    if 'usuario_id' not in session:
        return "Acesso negado! Faça login primeiro.", 401
    if session["perfil"] != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    return jsonify(UsuarioRepositorio.carregar_usuarios())

@app.route("/usuarios")
def buscar_usuarios():
    if 'usuario_id' not in session:
        return "Acesso negado! Faça login primeiro.", 401
    if session["perfil"] != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    usuarios = UsuarioRepositorio.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario_protegido(id):
    if session.get("perfil") != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    if UsuarioRepositorio.deletar_usuario_util(id):
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404

@app.route("/usuarios/", methods=["PUT"])
def atualizar_usuario_protegido():
    if "id_usuario" not in session:
        return "Acesso negado! Faça login primeiro.", 401
    
    usuario_edit = request.get_json()
    if UsuarioRepositorio.atualizar_usuario(session["id_usuario"], usuario_edit):
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado ou erro na atualização!"}), 404

@app.route("/admin")
def admin_area():
    if session.get("perfil") != "admin":
        return redirect(url_for("home"))
    return "Bem-vindo à área administrativa!"

if __name__ == "__main__":
    app.run(debug=True)
    