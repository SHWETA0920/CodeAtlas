from flask import Flask
from flask_cors import CORS
from config import SECRET_KEY, DEBUG
from api.ingest_routes import ingest_bp
from api.query_routes import query_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(ingest_bp, url_prefix="/api")
    app.register_blueprint(query_bp,  url_prefix="/api")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "devbrain-ai"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
