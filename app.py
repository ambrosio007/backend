from flask import Flask
from controller.usuario_controller import usuario_bp
from flask_jwt_extended import JWTManager, get_jwt, jwt_required
from datetime import timedelta, timezone
import datetime
from config import BLOCKLIST 
from controller.usuario_controller import usuario_bp

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secreta-chave-do-token-12345"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BLOCKLIST

app.register_blueprint(usuario_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0',  debug=False)
