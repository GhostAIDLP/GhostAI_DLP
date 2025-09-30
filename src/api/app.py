from flask import Flask, jsonify
from api.routers.risk import bp as risk_bp

def create_app():
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def healthz():
        return jsonify(ok=True), 200

    app.register_blueprint(risk_bp)
    return app
