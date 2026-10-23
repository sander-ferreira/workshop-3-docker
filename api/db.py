"""Connexion à MySQL : une connexion par requête HTTP, fermée à la fin de la requête."""

import os

import pymysql
from flask import g


def get_db():
    """Ouvre la connexion au premier appel de la requête, puis la réutilise."""
    if "db" not in g:
        g.db = pymysql.connect(
            host=os.environ["DB_HOST"],
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,  # lignes renvoyées sous forme de dict
            autocommit=True,
        )
    return g.db


def close_db(exc=None):
    """Appelée automatiquement par Flask à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
