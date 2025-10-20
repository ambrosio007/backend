from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

import uuid

import bcrypt

from repository.usuario_repository import UsuarioRepository

from service.usuario_service import UsuarioService

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route("/")
def home():
    return render_template("form.html")

@usuario_bp.route("/login")
def login():
    return render_template("login.html")

@usuario_bp.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    dados = request.form.to_dict()
    
    # 💥 AGORA CHAMA O SERVICE! 💥
    status = UsuarioService.cadastrar(dados)
    
    if status:
        return f"Usuário '{dados.get('nome')}' cadastrado com sucesso!"
    else:
        return "Não foi possível cadastrar o usuário!", 400

@usuario_bp.route("/usuarios/json")
def usuarios_json():
    usuarios = UsuarioRepository.carregar_usuarios()
    return jsonify(usuarios)

@usuario_bp.route("/listar-usuarios")
def listar_usuarios():
    usuarios = UsuarioRepository.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    sucesso = UsuarioRepository.deletar_usuario_util(id)
    if sucesso:
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    else:
        return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404

@usuario_bp.route("/editar-usuario/<id>")
def editar_usuario(id): # Mudei o nome para evitar confusão
    usuarios = UsuarioRepository.carregar_usuarios()
    usuario = next((u for u in usuarios if str(u['id']) == str(id)), None)
    if usuario:
        return render_template("editar_usuario.html", usuario=usuario)
    else:
        return "Usuário não encontrado!", 404
    
@usuario_bp.route("/usuarios/<id>", methods=["PUT"])
def atualizar_usuario_api(id):
    import bcrypt # Certifique-se de que está importado no topo do arquivo
    
    novos_dados = request.get_json() 
    
    if not novos_dados:
        return jsonify({"message": "Dados inválidos!"}), 400
    
    # Lógica de criptografia da senha (se a senha estiver sendo atualizada)
    if 'senha' in novos_dados:
        senha_hash = bcrypt.hashpw(
            novos_dados['senha'].encode('utf-8'), 
            bcrypt.gensalt()
        )
        novos_dados['senha'] = senha_hash.decode('utf-8')
    
    sucesso = UsuarioRepository.atualizar_usuario(id, novos_dados)
    if sucesso:
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    else:
        # Nota: Se o Postman receber este erro, pode ser que o ID não exista ou que haja um erro no SQL do Repositório.
        return jsonify({"message": "Usuário não encontrado ou erro na atualização!"}), 404
    
# ----------------- Login / Logout ----------------- #

@usuario_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioRepository.buscar_por_email(email)
    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
        session['usuario_id'] = usuario['id']
        session['perfil'] = usuario['perfil']
        return f"Login bem-sucedido! Bem-vindo, {usuario['nome']}."
    return "Email ou senha incorretos!", 401

@usuario_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------- Rotas Protegidas ----------------- #

@usuario_bp.route("/usuarios/json")
def buscar_usuarios_json():
    if 'usuario_id' not in session:
        return "Acesso negado! Faça login primeiro.", 401
    if session["perfil"] != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    return jsonify(UsuarioRepository.carregar_usuarios())

@usuario_bp.route("/usuarios")
def buscar_usuarios():
    if 'usuario_id' not in session:
        return "Acesso negado! Faça login primeiro.", 401
    if session["perfil"] != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    usuarios = UsuarioRepository.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario_protegido(id):
    if session.get("perfil") != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    if UsuarioRepository.deletar_usuario_util(id):
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404

@usuario_bp.route("/usuarios/", methods=["PUT"])
def atualizar_usuario_protegido():
    if "id_usuario" not in session:
        return "Acesso negado! Faça login primeiro.", 401
    
    usuario_edit = request.get_json()
    if UsuarioRepository.atualizar_usuario(session["id_usuario"], usuario_edit):
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado ou erro na atualização!"}), 404

@usuario_bp.route("/admin")
def admin_area():
    if session.get("perfil") != "admin":
        return redirect(url_for("home"))
    return "Bem-vindo à área administrativa!"