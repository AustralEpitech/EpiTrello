# EpiTrello

## How to Run

### Using Docker (recommended)

```bash
docker-compose up
xdg-open http://localhost:8000
```

### Running on bare metal

1. (Optional) Create and activate a python virtual environment

```bash
python -m venv .venv
. .venv/bin/activate
```

2. Install dependencies & start the server

```bash
pip install -r requirements
DEBUG=1 python manage.py runserver
xdg-open http://localhost:8000
```

### Seed data (Development)

To populate the database with test data (users: admin, alice, bob):

```bash
python manage.py seed
```


## Real-time (Django Channels)

EpiTrello supporte le temps réel via WebSocket grâce à Django Channels.

- En développement local (sans Docker): rien à configurer. Sans variable `REDIS_URL`, l’application utilise un Channel Layer en mémoire (pas persistant), suffisant pour tester.
- En Docker (production‑like): un service Redis est inclus dans `compose.yaml`. Lancez:

```bash
docker-compose up --build
```

Cela démarre:
- Postgres (db)
- Redis (channel layer)
- L’app ASGI (Uvicorn)

La variable d’environnement `REDIS_URL` est automatiquement fournie au conteneur d’app.

### Fonctionnement
- Chaque tableau possède un groupe WS `board_<id>`.
- Le navigateur ouvre `ws://<host>/ws/boards/<id>/` sur la page du tableau.
- Les actions serveur (mise à jour/suppression/création de carte, réordonnancement, etc.) émettent des événements vers le groupe correspondant.

### Tests
La suite de tests inclut des tests de diffusion qui valident qu’un événement est bien envoyé lors d’une mise à jour/suppression de carte (sans nécessiter Redis ni un serveur WS).
