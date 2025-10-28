from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import uuid
import bcrypt
from repository.usuario_repository import UsuarioRepository
from service.usuario_service import UsuarioService
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity, 
    get_jwt,
    jwt_required as jwt_required_strict
)
from config import BLOCKLIST

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route("/")
def home():
    return render_template("inicio.html")

@usuario_bp.route("/login")
def login():
    return render_template("login.html")

@usuario_bp.route("/cadastro")
def cadastro_usuario_page():
    return render_template("form.html")

@usuario_bp.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    dados = request.form.to_dict()
    
    status = UsuarioService.cadastrar(dados)
    
    if status:
        return f"Usuário '{dados.get('nome')}' cadastrado com sucesso!"
    else:
        return "Não foi possível cadastrar o usuário!", 400

@usuario_bp.route("/usuarios/json")
def usuarios_json():
    usuarios = UsuarioRepository.carregar_usuarios()
    return jsonify(usuarios)

# ⚠️ ROTA REMOVIDA: Esta rota '/listar-usuarios' duplicada e não protegida foi removida.
# @usuario_bp.route("/listar-usuarios")
# def listar_usuarios():
#     usuarios = UsuarioRepository.carregar_usuarios()
#     return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/editar-usuario/<id>", methods=["GET"])
@jwt_required_strict()
def editar_usuario(id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    if claims.get("perfil") != "admin" and str(current_user_id) != str(id):
        return jsonify({"message": "Acesso negado! Você só pode editar seu próprio perfil."}), 403

    usuario = UsuarioRepository.buscar_por_id(id)
    if usuario:
        return render_template("editar_usuario.html", usuario=usuario)
    else:
        return jsonify({"message": "Usuário não encontrado!"}), 404
    
@usuario_bp.route("/usuarios/<id>", methods=["PUT"])
@jwt_required_strict()
def atualizar_usuario_api(id):
    claims = get_jwt()

    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Apenas administradores podem usar esta rota."}), 403
        
    novos_dados = request.get_json() 
    
    if not novos_dados:
        return jsonify({"message": "Dados inválidos!"}), 400
    
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
        return jsonify({"message": "Usuário não encontrado ou erro na atualização!"}), 404

@usuario_bp.route("/usuarios/me", methods=["PUT"])
@jwt_required_strict()
def atualizar_proprio_usuario_api():
    """Permite que qualquer usuário logado atualize seu próprio perfil."""
    current_user_id = get_jwt_identity()
    novos_dados = request.get_json() 

    if not novos_dados:
        return jsonify({"message": "Dados inválidos!"}), 400
    
    # Hashea a senha se ela estiver presente nos dados
    if 'senha' in novos_dados and novos_dados['senha']:
        senha_hash = bcrypt.hashpw(
            novos_dados['senha'].encode('utf-8'), 
            bcrypt.gensalt()
        )
        novos_dados['senha'] = senha_hash.decode('utf-8')
        
    # Garante que um usuário normal não possa mudar o próprio perfil via esta rota, se 'perfil' estiver no payload
    if 'perfil' in novos_dados and get_jwt().get("perfil") != "admin":
        del novos_dados['perfil']

    sucesso = UsuarioRepository.atualizar_usuario(current_user_id, novos_dados)
    if sucesso:
        return jsonify({"message": "Seu perfil foi atualizado com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro na atualização do perfil!"}), 404

# ----------------- Login / Logout ----------------- #

@usuario_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioRepository.buscar_por_email(email)
    
    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
        additional_claims = {"perfil": usuario['perfil']}
        access_token = create_access_token(
            identity=usuario['id'], 
            additional_claims=additional_claims
        )
        
        # 🚨 CORREÇÃO: Retorna o token E o perfil para que o JS possa decidir o redirecionamento.
        return jsonify({
            "message": f"Login bem-sucedido! Bem-vindo, {usuario['nome']}.",
            "access_token": access_token,
            "perfil": usuario['perfil'] 
        }), 200
    
    return "Email ou senha incorretos!", 401

@usuario_bp.route("/logout", methods=["POST"])
@jwt_required_strict()
def logout():
    jti = get_jwt()["jti"]

    BLOCKLIST.add(jti)

    return jsonify({"message": "Logout bem-sucedido! Token revogado."}), 200

''' @usuario_bp.route("/logout", methods=["GET"])
def logout_redirect():
    return render_template("logout.html") '''

# ----------------- Rotas Protegidas (AGORA FUNCIONAIS COM REDIRECIONAMENTO) ----------------- 

@usuario_bp.route("/usuarios/json", methods=["GET"])
@jwt_required_strict()
def buscar_usuarios_json():
    claims = get_jwt()
    
    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Você não tem permissão de administrador."}), 403

    usuarios = UsuarioRepository.carregar_usuarios()
    return jsonify(usuarios)

#@usuario_bp.route("/usuarios")
#def buscar_usuarios():
#    if 'usuario_id' not in session:
#        return "Acesso negado! Faça login primeiro.", 401
#    if session["perfil"] != "admin":
#        return "Acesso negado! Você não tem permissão.", 403
#    usuarios = UsuarioRepository.carregar_usuarios()
#    return render_template("usuarios.html", usuarios=usuarios)


@usuario_bp.route("/listar-usuarios", methods=["GET"])
@jwt_required(optional=True) 
def listar_usuarios_protegido():
    claims = get_jwt()
    
    if not claims:

        return redirect(url_for('usuario.login')) 
              
    usuarios = UsuarioRepository.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)


@usuario_bp.route("/usuarios/<id>", methods=["DELETE"])
@jwt_required_strict()
def excluir_usuario_protegido(id):
    claims = get_jwt()

    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Você não tem permissão de administrador."}), 403
        
    if UsuarioRepository.deletar_usuario_util(id):
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404