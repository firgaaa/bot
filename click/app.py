"""
API Click & Collect KFC - Point d'entrée Flask.
Utilise ressource/ pour les appels API KFC.
"""
import os
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

# Charger .env depuis le dossier click
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path)

app = Flask(__name__)

# Configuration base de données depuis .env
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

# Initialiser le pool DB au démarrage
from utils.db import init_db

init_db(app)
app.config["DB_HOST"] = os.getenv("DB_HOST", "localhost")
app.config["DB_PORT"] = os.getenv("DB_PORT", "5432")
app.config["DB_NAME"] = os.getenv("DB_NAME", "kfc_bot")
app.config["DB_USER"] = os.getenv("DB_USER", "postgres")
app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "root")

# Gestion des erreurs globales
from utils.responses import (
    success_response,
    error_response,
    ErrorCode,
)


def register_error_handlers(app: Flask) -> None:
    """Enregistre les handlers d'erreur pour ne jamais faire planter le serveur."""

    @app.errorhandler(404)
    def not_found(e):
        return error_response(
            ErrorCode.NOT_FOUND,
            message="Ressource non trouvée",
            http_status=404,
        )

    @app.errorhandler(500)
    def internal_error(e):
        return error_response(
            ErrorCode.INTERNAL_ERROR,
            message="Erreur interne du serveur",
            http_status=500,
        )

    @app.errorhandler(Exception)
    def handle_exception(e):
        return error_response(
            ErrorCode.INTERNAL_ERROR,
            message="Erreur inattendue",
            details={"detail": str(e)} if app.debug else {},
            http_status=500,
        )


register_error_handlers(app)


@app.route("/")
def index():
    return success_response({"status": "ok", "message": "KFC API Click & Collect"})


# Enregistrer les routes
from api.routes import register_routes
register_routes(app)


if __name__ == "__main__":
    app.run(debug=True)
