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

## OAuth Authentication (Google & GitHub)

EpiTrello supports OAuth authentication with Google and GitHub providers.

### Configuration

To enable OAuth authentication, you need to configure the providers in your `.env` file:

#### Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. Select **Web application** as the application type
6. Configure the authorized redirect URIs:
   - For local development: `http://localhost:8000/accounts/google/login/callback/`
   - For production: `https://yourdomain.com/accounts/google/login/callback/`
7. Copy the **Client ID** and **Client Secret**
8. Add them to your `.env` file:

```bash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

#### GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the application details:
   - **Application name**: EpiTrello (or your preferred name)
   - **Homepage URL**: `http://localhost:8000` (or your production URL)
   - **Authorization callback URL**: 
     - For local: `http://localhost:8000/accounts/github/login/callback/`
     - For production: `https://yourdomain.com/accounts/github/login/callback/`
4. Click **Register application**
5. Copy the **Client ID** and generate a **Client Secret**
6. Add them to your `.env` file:

```bash
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### Usage

Once configured, users will see **"Continue with Google"** and **"Continue with GitHub"** buttons on the login and signup pages. Users can authenticate using their Google or GitHub accounts without creating a separate password.

### Note for Development

If you don't configure OAuth credentials, the OAuth buttons will still appear but will not work. The traditional username/password authentication will continue to work normally.



## Real-time (Django Channels)

EpiTrello supporte le temps réel via WebSocket grâce à Django Channels.

- En développement local (sans Docker): rien à configurer. Sans variable `REDIS_URL`, l'application utilise un Channel Layer en mémoire (pas persistant), suffisant pour tester.
- En Docker (production‑like): un service Redis est inclus dans `compose.yaml`. Lancez:

```bash
docker-compose up --build
```

Cela démarre:
- Postgres (db)
- Redis (channel layer)
- L'app ASGI (Uvicorn)

La variable d'environnement `REDIS_URL` est automatiquement fournie au conteneur d'app.

### Fonctionnement
- Chaque tableau possède un groupe WS `board_<id>`.
- Le navigateur ouvre `ws://<host>/ws/boards/<id>/` sur la page du tableau.
- Les actions serveur (mise à jour/suppression/création de carte, réordonnancement, etc.) émettent des événements vers le groupe correspondant.

## Tests

### Running Tests

To run all tests:

```bash
python manage.py test
```

### Code Coverage

The project maintains ≥85% code coverage on backend Python code.

To run tests with coverage:

```bash
# Run tests with coverage
coverage run --source=boards,epitrello manage.py test

# Display coverage report in terminal
coverage report

# Generate HTML coverage report
coverage html
# Then open htmlcov/index.html in your browser
```

The coverage configuration is in `.coveragerc` and excludes:
- Migration files
- Test files themselves
- Admin and app configuration files
- Static files

### Test Organization

Tests are organized in multiple files:
- `boards/tests.py` - Core user flow tests (authentication, boards, cards, search, etc.)
- `boards/tests_checklists.py` - Checklist and subtask functionality
- `boards/tests_realtime.py` - Real-time broadcast tests (Channels)
- `boards/tests_search.py` - Global search functionality
- `boards/tests_additional.py` - Additional endpoint tests (reorder, labels, comments, notifications, export, error handling)
- `boards/tests_websocket.py` - WebSocket consumer tests

Total: **78 tests** covering all major functionality.

The test suite includes:
- Unit tests for all API endpoints
- Integration tests for user workflows
- WebSocket connection and broadcast tests
- Permission and access control tests
- Error handling and validation tests
