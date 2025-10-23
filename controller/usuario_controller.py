from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import uuid
import bcrypt
from repository.usuario_repository import UsuarioRepository
from service.usuario_service import UsuarioService
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route("/")
def home():
    return render_template("inicio.html")

@usuario_bp.route("/login")
def login():
    return render_template("login.html")

@usuario_bp.route("/cadastro") # Nova rota GET para exibir o formulário
def cadastro_usuario_page():
    # O seu template de cadastro parece ser o "form.html"
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

@usuario_bp.route("/editar-usuario/<id>", methods=["GET"])
@jwt_required()
def editar_usuario(id):
    # Permite a edição se for admin OU se o ID for do próprio usuário logado
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
@jwt_required()
def atualizar_usuario_api(id):
    # Apenas administradores podem atualizar perfis de outros usuários.
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
    
# ----------------- Login / Logout ----------------- #

@usuario_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = UsuarioRepository.buscar_por_email(email)
    
    if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
        # 🚀 SUCESSO: Cria o token JWT.
        # Identity é o ID do usuário. Claims são informações adicionais (perfil).
        additional_claims = {"perfil": usuario['perfil']}
        access_token = create_access_token(
            identity=usuario['id'], 
            additional_claims=additional_claims
        )
        
        # Retorna o token para o cliente, que deve incluí-lo nos headers de futuras requisições
        return jsonify({
            "message": f"Login bem-sucedido! Bem-vindo, {usuario['nome']}.",
            "access_token": access_token
        }), 200
    
    return "Email ou senha incorretos!", 401

@usuario_bp.route("/logout")
def logout():
    # Para JWT, o logout ocorre no cliente (excluindo o token armazenado).
    # Esta rota pode ser usada apenas para redirecionar para a página de login.
    return redirect(url_for('usuario.login'))

# ----------------- Rotas Protegidas ----------------- #

@usuario_bp.route("/usuarios/json", methods=["GET"])
@jwt_required()
def buscar_usuarios_json():
    claims = get_jwt()
    
    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Você não tem permissão de administrador."}), 403

    usuarios = UsuarioRepository.carregar_usuarios()
    return jsonify(usuarios)

@usuario_bp.route("/usuarios")
def buscar_usuarios():
    if 'usuario_id' not in session:
        return "Acesso negado! Faça login primeiro.", 401
    if session["perfil"] != "admin":
        return "Acesso negado! Você não tem permissão.", 403
    usuarios = UsuarioRepository.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/listar-usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios_protegido():
    claims = get_jwt()
    
    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Você não tem permissão de administrador."}), 403
        
    usuarios = UsuarioRepository.carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@usuario_bp.route("/usuarios/<id>", methods=["DELETE"])
@jwt_required()
def excluir_usuario_protegido(id):
    claims = get_jwt()

    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Você não tem permissão de administrador."}), 403
        
    if UsuarioRepository.deletar_usuario_util(id):
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404

@usuario_bp.route("/usuarios/me", methods=["PUT"])
@jwt_required()
def atualizar_usuario_protegido():
    current_user_id = get_jwt_identity()
    novos_dados = request.get_json() 

    if not novos_dados:
        return jsonify({"message": "Dados inválidos!"}), 400
    
    if 'senha' in novos_dados:
        senha_hash = bcrypt.hashpw(
            novos_dados['senha'].encode('utf-8'), 
            bcrypt.gensalt()
        )
        novos_dados['senha'] = senha_hash.decode('utf-8')
    
    sucesso = UsuarioRepository.atualizar_usuario(current_user_id, novos_dados)
    if sucesso:
        return jsonify({"message": "Seu perfil foi atualizado com sucesso!"}), 200
    else:
        return jsonify({"message": "Erro na atualização do perfil!"}), 404

    if claims.get("perfil") != "admin":
        return jsonify({"message": "Acesso negado! Você não tem permissão de administrador."}), 403
        
    return "Bem-vindo à área administrativa!"

@usuario_bp.route("/dashboard")
@jwt_required()
def dashboard():
    """
    Rota de destino após o login.
    Redireciona administradores diretamente para a lista de usuários.
    """
    claims = get_jwt()
    
    # Verifica se o usuário logado tem o perfil de administrador
    if claims.get("perfil") == "admin":
        # Redireciona para a rota protegida de listagem de usuários
        # O nome do endpoint é 'usuario.listar_usuarios_protegido'
        return redirect(url_for('usuario.listar_usuarios_protegido'))
    
    # Se não for admin, você pode redirecionar para a home ou uma página de perfil pessoal
    else:
        # Sugestão: Redireciona para a página inicial (home)
        return redirect(url_for('usuario.home'))