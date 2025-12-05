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
