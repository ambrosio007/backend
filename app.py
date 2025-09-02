from flask import Flask
from controller.usuario_controller import usuario_bp


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

app.register_blueprint(usuario_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0',  debug=False)

    