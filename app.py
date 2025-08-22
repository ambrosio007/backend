from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)

def carregar_usuarios():
    try:
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        else:
            return []
    except (IOError, json.JSONDecodeError):
        return []

def salvar_usuario(usuario):
    usuarios = carregar_usuarios()
    try:
        usuarios.append(usuario)
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)
        return True
    except (IOError, TypeError):
        return False

def deletar_usuario_util(id):
    usuarios = carregar_usuarios()
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.get("id") != id]
    
    if len(usuarios) == len(usuarios_filtrados):
        return False
    
    try:
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios_filtrados, arquivo, indent=4)
        return True
    except (IOError, TypeError):
        return False

def atualizar_usuario(id_usuario, novos_dados):

    usuarios = carregar_usuarios()
    usuario_encontrado = False
    for i, usuario in enumerate(usuarios):
        if str(usuario['id']) == str(id_usuario): 
            usuarios[i].update(novos_dados)
            usuario_encontrado = True
            break
    
    if not usuario_encontrado:
        return False 
    
    try:
        with open("usuarios.json", "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4)
        return True
    except (IOError, TypeError):
        return False


@app.route("/")
def home():
    return render_template("form.html")

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
    
    status = salvar_usuario(usuario)
    
    if status:
        return f"Usuário '{usuario['nome']}' cadastrado com sucesso!"
    else:
        return "Não foi possível cadastrar o usuário!"

@app.route("/usuarios/json")
def usuarios_json():
    usuarios = carregar_usuarios()
    return jsonify(usuarios)

@app.route("/listar-usuarios")
def listar_usuarios():
    usuarios = carregar_usuarios()
    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/usuarios/<id>", methods=["DELETE"])
def excluir_usuario(id):
    sucesso = deletar_usuario_util(id)
    if sucesso:
        return jsonify({"message": "Usuário excluído com sucesso!"}), 200
    else:
        return jsonify({"message": "Usuário não encontrado ou erro na exclusão!"}), 404

@app.route("/editar-usuario/<id>")
def editar_usuario(id):
    usuarios = carregar_usuarios()
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
    
    sucesso = atualizar_usuario(id, novos_dados)
    if sucesso:
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    else:
        return jsonify({"message": "Usuário não encontrado ou erro na atualização!"}), 404

if __name__ == "__main__":
    app.run(debug=True)
