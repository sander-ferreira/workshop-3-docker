"""API Adresses : point d'entrée Flask.

Les routes sont séparées selon le front qui les appelle :
  /api/admin/...  -> front administrateur (liste, création, suppression)
  /api/users/...  -> front utilisateurs (lecture seule)
"""

import logging

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from db import close_db, get_db
from routes.admin import admin_bp
from routes.users import users_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("api")

app = Flask(__name__)
app.teardown_appcontext(close_db)

app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(users_bp, url_prefix="/api/users")


@app.get("/api/health")
def health():
    """Utilisée par le HEALTHCHECK Docker : vérifie aussi que MySQL répond."""
    with get_db().cursor() as cur:
        cur.execute("SELECT 1")
    return {"status": "ok"}


@app.errorhandler(HTTPException)
def http_error(e):
    """Erreurs HTTP (404, 405...) renvoyées en JSON plutôt qu'en HTML."""
    return jsonify(error=e.description), e.code


@app.errorhandler(Exception)
def server_error(e):
    log.exception("erreur non gérée")
    return jsonify(error="Erreur interne du serveur"), 500
