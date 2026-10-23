"""Routes du front administrateur, préfixées par /api/admin."""

import re
from datetime import timezone

from flask import Blueprint, abort, request

from db import get_db

admin_bp = Blueprint("admin", __name__)

# Champ -> longueur max (identique aux colonnes de la table)
FIELDS = {"numero_rue": 10, "nom_rue": 255, "ville": 100, "code_postal": 5}


def validate(data):
    """Vérifie le JSON envoyé par le front et Renvoie (adresse, erreurs)."""
    if not isinstance(data, dict):
        return None, {"body": "Un objet JSON est attendu"}

    adresse, errors = {}, {}
    for field, max_len in FIELDS.items():
        value = str(data.get(field) or "").strip()
        if not value:
            errors[field] = "Champ obligatoire"
        elif len(value) > max_len:
            errors[field] = f"{max_len} caractères maximum"
        adresse[field] = value

    if "code_postal" not in errors and not re.fullmatch(r"\d{5}", adresse["code_postal"]):
        errors["code_postal"] = "5 chiffres attendus"
    return adresse, errors


@admin_bp.get("/adresses")
def list_adresses():
    with get_db().cursor() as cur:
        cur.execute(
            "SELECT id, numero_rue, nom_rue, ville, code_postal, created_at "
            "FROM adresse ORDER BY id DESC"
        )
        # list() : fetchall() renvoie un tuple vide si aucun résultat, que Flask refuserait
        adresses = list(cur.fetchall())
    for a in adresses:
        # MySQL renvoie le TIMESTAMP en UTC (fuseau du conteneur) : on le précise pour le navigateur
        a["created_at"] = a["created_at"].replace(tzinfo=timezone.utc).isoformat()
    return adresses


@admin_bp.post("/adresses")
def create_adresse():
    adresse, errors = validate(request.get_json(silent=True))
    if errors:
        return {"errors": errors}, 400

    # Requête paramétrée (%s) : pymysql échappe les valeurs, pas d'injection SQL possible
    with get_db().cursor() as cur:
        cur.execute(
            "INSERT INTO adresse (numero_rue, nom_rue, ville, code_postal) VALUES (%s, %s, %s, %s)",
            (adresse["numero_rue"], adresse["nom_rue"], adresse["ville"], adresse["code_postal"]),
        )
        adresse["id"] = cur.lastrowid
    return adresse, 201


@admin_bp.delete("/adresses/<int:adresse_id>")
def delete_adresse(adresse_id):
    with get_db().cursor() as cur:
        deleted = cur.execute("DELETE FROM adresse WHERE id = %s", (adresse_id,))
    if not deleted:
        abort(404, "Adresse introuvable")
    return "", 204
