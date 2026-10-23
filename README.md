# Workshop 3 - Architecture microservices complète

Gestion d'adresses en microservices avec Docker Compose : une base MySQL, une API, un front administrateur (création), un front utilisateurs (consultation), un reverse-proxy et un système de migrations SQL.

## Lancement

```bash
docker compose up -d --build
```

| URL | Service |
| --- | --- |
| http://localhost/ | Front utilisateurs (consultation, recherche par ville) |
| http://localhost/admin/ | Front administrateur (création, suppression) |
| http://localhost/api/health | État de l'API et de la base |

Arrêt : `docker compose down` (ajouter `-v` pour supprimer aussi les données MySQL).

## Architecture

```
                         ┌──────────────── réseau frontend ────────────────┐
navigateur ──:80──> reverse_proxy ──/────────> front_users  (nginx, statique)
                         │        ──/admin/──> front_admin  (nginx, statique)
                         │        ──/api/────> api          (Flask + gunicorn)
                         └─────────────────────────────────────│───────────┘
                                                               │
                         ┌──────── réseau backend (internal) ──│───────────┐
                         │   migrations (Flyway) ──> db (MySQL 8.4) <──────┘
                         └─────────────────────────────────────────────────┘
```

- **Seul `reverse_proxy` publie un port (80).** Les autres services utilisent `expose` : ils ne sont joignables que depuis les réseaux Docker.
- **Deux réseaux.** `frontend` relie le proxy, les fronts et l'API. `backend` relie l'API, la base et les migrations. Il est `internal: true` : pas d'accès à internet, et le proxy comme les fronts ne peuvent pas joindre la base.
- **Ordre de démarrage garanti par les healthchecks** : `db` healthy → `migrations` terminée avec succès → `api` healthy → fronts healthy → `reverse_proxy`.

## Structure

```
.
├── docker-compose.yml
├── .env / .env.example     # identifiants MySQL
├── migrations/             # fichiers SQL versionnés (Flyway)
├── api/                    # microservice API (Python / Flask)
│   ├── app.py              # création de l'app, health, gestion des erreurs
│   ├── db.py               # connexion MySQL
│   └── routes/
│       ├── admin.py        # /api/admin/...
│       └── users.py        # /api/users/...
├── front_admin/            # HTML/CSS/JS servi par nginx
├── front_users/            # HTML/CSS/JS servi par nginx
└── reverse_proxy/          # nginx.conf du point d'entrée
```

## Routes de l'API

Les routes sont différenciées par préfixe selon le front appelant :

| Méthode | Route | Front | Rôle |
| --- | --- | --- | --- |
| GET | `/api/admin/adresses` | admin | Liste complète (avec date de création) |
| POST | `/api/admin/adresses` | admin | Crée une adresse (validation côté serveur) |
| DELETE | `/api/admin/adresses/<id>` | admin | Supprime une adresse |
| GET | `/api/users/adresses?ville=...` | users | Liste en lecture seule, filtrable par ville |
| GET | `/api/health` | Docker | Healthcheck (vérifie aussi MySQL) |

Exemple de création :

```bash
curl -X POST http://localhost/api/admin/adresses \
  -H 'Content-Type: application/json' \
  -d '{"numero_rue":"3","nom_rue":"Rue de la Paix","ville":"Paris","code_postal":"75002"}'
```

## Migrations

Le service `migrations` (image officielle Flyway) applique au démarrage les fichiers de `migrations/`, dans l'ordre de leur version :

| Fichier | Contenu |
| --- | --- |
| `V1__create_table_adresse.sql` | Table `adresse` |
| `V2__insert_adresses_exemple.sql` | Données de départ |
| `V3__index_ville.sql` | Index pour la recherche par ville |

Flyway enregistre chaque migration appliquée dans la table `flyway_schema_history`. Au démarrage suivant, il n'applique que les nouvelles. Pour faire évoluer le schéma, il suffit d'ajouter un fichier `V4__....sql`. Un fichier déjà appliqué ne doit jamais être modifié : Flyway contrôle sa somme de contrôle et refuse de démarrer s'il a changé.

## Bonnes pratiques appliquées

- Versions d'images figées (`mysql:8.4.13`, `nginx:1.30.6-alpine`, `python:3.13.17-slim`, `flyway/flyway:13.11.1`) et images construites taguées (`workshop3/api:1.0.0`, ...).
- Dépendances Python figées dans `requirements.txt`.
- API exécutée par un utilisateur non-root, avec gunicorn comme serveur de production.
- Healthchecks sur tous les services longue durée, `restart: unless-stopped`.
- Identifiants hors du code, dans `.env`. L'API utilise un compte MySQL dédié, pas `root`.
- Données MySQL persistées dans un volume nommé (`db_data`).
- Requêtes SQL paramétrées (pas d'injection), affichage via `textContent` côté front (pas de XSS).
