"""Routes du front utilisateurs, préfixées par /api/users : lecture seule."""

from flask import Blueprint, request

from db import get_db

users_bp = Blueprint("users", __name__)


@users_bp.get("/adresses")
def list_adresses():
    """Liste des adresses, filtrable par ville : /api/users/adresses?ville=par"""
    # Pas de created_at ici : les utilisateurs ne voient que l'adresse elle-même
    sql = "SELECT id, numero_rue, nom_rue, ville, code_postal FROM adresse"
    params = ()

    ville = request.args.get("ville", "").strip()
    if ville:
        sql += " WHERE ville LIKE %s"
        params = (f"%{ville}%",)

    with get_db().cursor() as cur:
        cur.execute(sql + " ORDER BY ville, nom_rue", params)
        # list() : fetchall() renvoie un tuple vide si aucun résultat, que Flask refuserait
        return list(cur.fetchall())
