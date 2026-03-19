"""
Format standard des réponses API et gestion des erreurs.
"""
from typing import Any, Optional

from flask import jsonify, Response


# Codes d'erreur
class ErrorCode:
    SESSION_ALREADY_EXISTS = "SESSION_ALREADY_EXISTS"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    NOT_FOUND = "NOT_FOUND"
    INVALID_STATE = "INVALID_STATE"
    KFC_API_ERROR = "KFC_API_ERROR"
    RECAPTCHA_FAILED = "RECAPTCHA_FAILED"
    STORE_NOT_FOUND = "STORE_NOT_FOUND"
    STORE_NOT_SUPPORTED = "STORE_NOT_SUPPORTED"
    LOYALTY_MENU_UNAVAILABLE = "LOYALTY_MENU_UNAVAILABLE"
    CHECKIN_NOT_POSSIBLE = "CHECKIN_NOT_POSSIBLE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSUFFICIENT_POINTS = "INSUFFICIENT_POINTS"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# Messages par défaut
DEFAULT_MESSAGES = {
    ErrorCode.SESSION_ALREADY_EXISTS: "Une session existe déjà pour ce panier",
    ErrorCode.SESSION_NOT_FOUND: "Aucune session trouvée pour ce panier",
    ErrorCode.NOT_FOUND: "Ressource non trouvée",
    ErrorCode.INVALID_STATE: "Action impossible dans l'état actuel de la session",
    ErrorCode.KFC_API_ERROR: "Erreur lors de l'appel à l'API KFC",
    ErrorCode.RECAPTCHA_FAILED: "Échec de la validation reCAPTCHA",
    ErrorCode.STORE_NOT_FOUND: "Restaurant introuvable",
    ErrorCode.STORE_NOT_SUPPORTED: "Ce restaurant n'est pas supporté pour le Click & Collect",
    ErrorCode.LOYALTY_MENU_UNAVAILABLE: "Menu fidélité indisponible pour ce restaurant",
    ErrorCode.CHECKIN_NOT_POSSIBLE: "Le check-in n'est pas possible pour cette commande",
    ErrorCode.VALIDATION_ERROR: "Données invalides",
    ErrorCode.INSUFFICIENT_POINTS: "Points insuffisants",
    ErrorCode.INTERNAL_ERROR: "Erreur interne du serveur",
}


def success_response(data: Any = None, http_status: int = 200) -> tuple[Response, int]:
    """
    Réponse de succès standard.
    Format : { "success": true, "data": ..., "error": null }
    """
    return jsonify({
        "success": True,
        "data": data,
        "error": None,
    }), http_status


def error_response(
    code: str,
    message: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    http_status: int = 400,
) -> tuple[Response, int]:
    """
    Réponse d'erreur standard.
    Format : { "success": false, "data": null, "error": { "code", "message", "details" } }
    """
    msg = message or DEFAULT_MESSAGES.get(code, "Erreur inconnue")
    return jsonify({
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": msg,
            "details": details or {},
        },
    }), http_status


def handle_api_errors(f):
    """
    Décorateur pour capturer les exceptions et retourner une réponse d'erreur.
    Empêche le serveur de planter.
    """
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return error_response(
                ErrorCode.VALIDATION_ERROR,
                message=str(e),
                http_status=400,
            )
        except Exception as e:
            return error_response(
                ErrorCode.INTERNAL_ERROR,
                message="Erreur interne",
                details={"detail": str(e)} if __debug__ else {},
                http_status=500,
            )
    return wrapper
