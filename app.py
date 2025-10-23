from flask import Flask
from controller.usuario_controller import usuario_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secreta-chave-do-token-12345"

jwt = JWTManager(app)

app.register_blueprint(usuario_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0',  debug=False)

    