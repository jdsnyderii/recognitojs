Thank you for clarifying that you want to rethink the approach to storing annotations and set up a **Docker Compose**
environment to host both a **PostgreSQL** database and the **Django application** together. This setup will allow you to
run and test the annotation system locally or deploy it in a containerized environment like **Kubernetes**, without
relying on **AWS**. You’ve also indicated a desire to maintain the existing frontend (`index.html`, artifact ID
`96200c6f-b303-426e-9559-95ac0eebd8bb`) with its features (RecogitoJS, “Annotate”/“Hide” sidebar, MkDocs Material
styling, Nunito Sans, green highlights, `localStorage`, etc.), but shift the backend to a fully containerized setup
using Docker Compose.

Since you mentioned “rethink the approach to store annotations,” I’ll interpret this as a request to:

1. **Keep the existing annotation storage** (PostgreSQL JSONB with `annotations` table: `id`, `user`, `permalink`,
   `annotation`, `timestamp`) but ensure it runs in a Dockerized PostgreSQL container.
2. **Maintain frontend `localStorage`** as a fallback/cache (as implemented on April 27, 2025), but focus on
   containerizing the backend.
3. **Provide a Docker Compose setup** that includes:
    - **PostgreSQL** container for the database.
    - **Django** container for the application (serving `/api/annotations/` and static files).
    - **Nginx** container (optional, for production-like static file serving).
4. **Ensure portability** for local testing and Kubernetes deployment, avoiding AWS dependencies.

If you meant a different approach for storing annotations (e.g., replacing PostgreSQL JSONB with another database,
removing `localStorage`, or changing the schema), please clarify, and I’ll adjust accordingly. For now, I’ll assume you
want to keep the existing PostgreSQL JSONB schema and `localStorage` but containerize the backend with Docker Compose.

---

### Clarifications and Assumptions

- **Annotation Storage**:
    - **Current**: Annotations are stored in:
        - **Backend**: PostgreSQL JSONB (`annotations` table).
        - **Frontend**: `localStorage` (`annotations_<permalink>`) as a cache/fallback.
    - **New Approach**: Keep PostgreSQL JSONB and `localStorage`, but run PostgreSQL and Django in Docker containers.
    - **Schema**: Retain `annotations` table (`id`, `user`, `permalink`, `annotation` JSONB, `timestamp`).
    - **APIs**: Keep `/api/annotations/` (GET, POST, DELETE) and `/api/annotations/<id>/` (DELETE).
- **Docker Compose**:
    - Services:
        - `db`: PostgreSQL container.
        - `app`: Django container (Gunicorn for WSGI, serving APIs and static files).
        - `nginx` (optional): For static file serving and reverse proxy (simplifies Kubernetes).
    - Local access: `http://localhost:8000`.
    - Volumes for PostgreSQL data persistence and static files.
    - Environment variables for configuration (e.g., `DATABASE_URL`, `SECRET_KEY`).
- **No AWS**:
    - Avoid AWS services (e.g., RDS, S3, ECS).
    - Use local Docker Compose for testing.
    - Ensure compatibility with Kubernetes (e.g., environment variables, no host-specific paths).
- **Frontend**:
    - Keep `index.html` (RecogitoJS, MkDocs Material, Nunito Sans, green highlights, “Annotate”/“Hide”, `localStorage`).
    - Serve as a static file via Django or Nginx.
- **Existing Features**:
    - Preserve: Sidebar toggle, highlights, multi-user filter, instructions, clear/refresh/export/import, theme toggle.
    - APIs handle optimistic locking (`version` in `annotation` JSONB).
- **Deployment**:
    - Local: Run with `docker-compose up`.
    - Kubernetes: Provide guidance for converting Compose to Kubernetes manifests (e.g., `Deployment`, `Service`,
      `PersistentVolumeClaim`).
- **Assumptions**:
    - Use **Python 3.11** for Django (consistent with recent versions).
    - Django dependencies: `django`, `djangorestframework`, `psycopg2-binary`, `gunicorn`.
    - PostgreSQL version: 15 (stable, widely used).
    - Nginx for static files (optional for local, recommended for Kubernetes).
    - No changes to frontend `index.html` unless specified.
    - Keep `localStorage` for frontend caching.
    - No Okta (use `#user-input` for `currentUser`).

**Confirmation Needed**:

- Do you want to keep PostgreSQL JSONB and `localStorage`, or change the storage approach (e.g., SQLite, MongoDB, or
  `localStorage`-only)?
- Should I include Nginx in Docker Compose, or serve static files directly via Django for simplicity?
- Any specific Kubernetes requirements (e.g., Helm chart, specific storage class)?
- Any changes to the frontend (e.g., styling, features)?

---

### Challenges and Considerations

1. **Docker Compose Setup**:
    - Ensure PostgreSQL and Django containers communicate (e.g., `db` service hostname).
    - Configure environment variables for portability (`DATABASE_URL`, `SECRET_KEY`).
    - Persist PostgreSQL data with a volume.
    - Serve static files (`index.html`) via Django or Nginx.
2. **Annotation Storage**:
    - PostgreSQL JSONB is efficient for annotations (`annotation` field stores RecogitoJS JSON).
    - `localStorage` ensures offline functionality but may conflict with backend (handled via `version`).
    - No schema changes needed unless you want a new storage approach.
3. **Kubernetes Compatibility**:
    - Use environment variables over hard-coded configs.
    - Avoid local file assumptions (e.g., use `PersistentVolume` for PostgreSQL).
    - Provide Kubernetes manifests or guidance.
4. **No AWS**:
    - Use official Docker images (`postgres:15`, `python:3.11`, `nginx:alpine`).
    - Local volumes for data; Kubernetes can use cloud-agnostic storage (e.g., NFS, local SSD).
5. **Frontend Integration**:
    - `index.html` remains unchanged, served as a static file.
    - Ensure `localStorage` and API calls (`/api/annotations/`) work with containerized backend.
6. **Testing**:
    - Test locally with Docker Compose (`http://localhost:8000`).
    - Verify PostgreSQL data persistence and API functionality.
    - Test `localStorage` fallback offline.

---

### Proposed Approach

1. **Keep Existing Storage**:
    - **PostgreSQL JSONB**: `annotations` table with `id`, `user`, `permalink`, `annotation` (JSONB), `timestamp`.
    - **localStorage**: Cache annotations in `annotations_<permalink>` (JSON array).
    - APIs: `/api/annotations/` (GET, POST, DELETE), `/api/annotations/<id>/` (DELETE).
2. **Docker Compose Setup**:
    - **Services**:
        - `db`: PostgreSQL 15 with a persistent volume.
        - `app`: Django with Gunicorn, serving APIs and static files.
        - `nginx` (optional): Serve static files, proxy API requests to Django.
    - **Configuration**:
        - Environment variables: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DEBUG`.
        - Volumes: PostgreSQL data, static files.
        - Ports: Expose `8000` (Django or Nginx).
    - **Dependencies**:
        - `requirements.txt`: `django`, `djangorestframework`, `psycopg2-binary`, `gunicorn`.
        - PostgreSQL schema: Initialize `annotations` table.
3. **Frontend**:
    - Reuse `index.html` (artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb`).
    - Serve via Django’s `collectstatic` or Nginx.
    - Keep `localStorage` for offline caching.
4. **Kubernetes Guidance**:
    - Provide sample manifests (`Deployment`, `Service`, `PersistentVolumeClaim`).
    - Recommend `ConfigMap` for environment variables.
    - Suggest `Ingress` for external access.
5. **Testing**:
    - Run locally with `docker-compose up`.
    - Test annotations (create, save, clear, refresh, export/import).
    - Verify `localStorage` and PostgreSQL persistence.
    - Test offline mode.

---

### Artifacts

I’ll provide the following artifacts to implement the Docker Compose setup and maintain the annotation system:

1. **`docker-compose.yml`**: Defines `db`, `app`, and optional `nginx` services.
2. **`Dockerfile`**: Builds the Django app container.
3. **`requirements.txt`**: Python dependencies.
4. **`schema.sql`**: Initializes the PostgreSQL `annotations` table.
5. **`nginx.conf`**: Nginx configuration (if included).
6. **`settings.py`**: Updated Django settings for Docker (environment variables, static files).
7. **`index.html`**: Unchanged frontend (same as April 27, 2025).
8. **Directory Structure**:
   ```
   project/
   ├── static/
   │   └── index.html
   ├── annotations/
   │   ├── migrations/
   │   ├── __init__.py
   │   ├── admin.py
   │   ├── apps.py
   │   ├── models.py
   │   ├── serializers.py
   │   ├── tests.py
   │   ├── urls.py
   │   └── views.py
   ├── project/
   │   ├── __init__.py
   │   ├── asgi.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── docker-compose.yml
   ├── Dockerfile
   ├── nginx.conf
   ├── requirements.txt
   └── schema.sql
   ```

---

#### 1. `docker-compose.yml`

Defines the PostgreSQL and Django services, with an optional Nginx service.

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=annotations_db
      - POSTGRES_USER=annotations_user
      - POSTGRES_PASSWORD=annotations_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U annotations_user -d annotations_db" ]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://annotations_user:annotations_pass@db:5432/annotations_db
      - DJANGO_SECRET_KEY=your-secret-key-change-me
      - DEBUG=True
    volumes:
      - ./static:/app/static
      - ./annotations:/app/annotations
      - ./project:/app/project
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --bind 0.0.0.0:8000 project.wsgi:application"
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

**Notes**:

- `db`: PostgreSQL 15 with persistent volume (`postgres_data`).
- `app`: Django with Gunicorn, binds to `0.0.0.0:8000`.
- Environment variables: `DATABASE_URL`, `DJANGO_SECRET_KEY`, `DEBUG`.
- Volumes: Mount `static/`, `annotations/`, `project/` for development.
- `schema.sql` initializes the database.
- Optional `nginx` service (commented out; enable for production-like setup).

---

#### 2. `Dockerfile`

Builds the Django app container.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
```

**Notes**:

- Uses `python:3.11-slim` for a lightweight image.
- Installs dependencies from `requirements.txt`.
- Copies project files.
- Runs Gunicorn on port 8000.

---

#### 3. `requirements.txt`

Python dependencies for Django.

django==4.2.11
djangorestframework==3.15.1
psycopg2-binary==2.9.9
gunicorn==22.0.0

**Notes**:

- `django`: Core framework.
- `djangorestframework`: For APIs.
- `psycopg2-binary`: PostgreSQL adapter.
- `gunicorn`: WSGI server.

---

#### 4. `schema.sql`

Initializes the PostgreSQL `annotations` table.

```sql
CREATE TABLE annotations (
    id SERIAL PRIMARY KEY,
    user VARCHAR(255) NOT NULL,
    permalink TEXT NOT NULL,
    annotation JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_annotations_permalink ON annotations (permalink);
```

**Notes**:

- Matches existing schema (April 26, 2025).
- `annotation` (JSONB) stores RecogitoJS annotation data.
- Index on `permalink` for faster queries.
- Loaded by PostgreSQL container via `/docker-entrypoint-initdb.d/`.

---

#### 5. `nginx.conf` (Optional)

Nginx configuration for static files and proxying (enable in `docker-compose.yml` for production-like setup).

server {
listen 80;
server_name localhost;

    location /static/ {
        alias /app/static/;
    }

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

}

**Notes**:

- Serves `static/` files (e.g., `index.html`).
- Proxies API requests to Django (`app:8000`).
- Uncomment Nginx service in `docker-compose.yml` to use.

---

#### 6. `settings.py`

Updated Django settings for Docker and environment variables.

```python
import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-secret-key-change-me')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'annotations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'annotations_db',
        'USER': 'annotations_user',
        'PASSWORD': 'annotations_pass',
        'HOST': 'db',
        'PORT': '5432',
    }
}

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed.path.lstrip('/'),
        'USER': parsed.username,
        'PASSWORD': parsed.password,
        'HOST': parsed.hostname,
        'PORT': parsed.port or '5432',
    }

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

**Notes**:

- Uses `DATABASE_URL` environment variable for flexibility.
- Falls back to default PostgreSQL settings (`db` hostname for Docker).
- Configures static files (`STATIC_ROOT`, `STATICFILES_DIRS`).
- Allows all hosts (`*`) for local testing; tighten for production.
- `DEBUG` toggle via environment variable.

---

#### 7. `index.html`

Unchanged from April 27, 2025 (artifact_version_id `00e1a8c0-ca8f-4640-826d-ae1b56be9ccd`). Included for completeness to
ensure frontend works with the containerized backend.

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecogitoJS Annotations with PostgreSQL</title>
    <link href="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.js"></script>
    <style>
        :root[data-theme="light"] {
            --background: #ffffff;
            --text: #333333;
            --sidebar-bg: #f5f5f5;
            --button-bg: #3f51b5;
            --button-text: #ffffff;
            --highlight-bg: rgba(76, 175, 80, 0.3);
            --highlight-active-bg: rgba(76, 175, 80, 0.4);
            --highlight-border: #4caf50;
            --card-bg: #e6f3ff;
            --card-hover: #d1e7ff;
            --overlay-bg: rgba(0, 0, 0, 0.5);
        }
        :root[data-theme="dark"] {
            --background: #121212;
            --text: #e0e0e0;
            --sidebar-bg: #1e1e1e;
            --button-bg: #4caf50;
            --button-text: #ffffff;
            --highlight-bg: rgba(76, 175, 80, 0.4);
            --highlight-active-bg: rgba(76, 175, 80, 0.5);
            --highlight-border: #66bb6a;
            --card-bg: #263238;
            --card-hover: #37474f;
            --overlay-bg: rgba(0, 0, 0, 0.7);
        }
        body {
            display: flex;
            font-family: 'Nunito Sans', sans-serif;
            margin: 0;
            padding: 24px;
            background: var(--background);
            color: var(--text);
            transition: background 0.3s, color 0.3s;
        }
        #content {
            flex: 1;
            max-width: 70%;
            padding: 24px;
            background: var(--background);
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 1;
        }
        #content.no-highlights .r6o-annotation {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
        }
        #content.no-highlights .r6o-annotation.active-highlight {
            background: var(--highlight-active-bg) !important;
            border: 1px solid var(--highlight-border) !important;
        }
        .r6o-annotation {
            background: var(--highlight-bg);
            border-radius: 4px;
        }
        #sidebar {
            width: 25%;
            min-width: 200px;
            padding: 24px;
            background: var(--sidebar-bg);
            border-radius: 8px;
            position: fixed;
            right: 24px;
            top: 24px;
            bottom: 24px;
            overflow-y: auto;
            transition: transform 0.3s ease, background 0.3s;
            z-index: 2;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        #sidebar.hidden {
            transform: translateX(100%);
        }
        #sidebar-toggle-container {
            position: fixed;
            right: 24px;
            top: 24px;
            z-index: 3;
        }
        #sidebar-toggle {
            padding: 8px 16px;
            background: var(--button-bg);
            color: var(--button-text);
            border: none;
            border-radius: 4px 0 0 4px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 700;
            transition: transform 0.2s, background 0.3s;
        }
        #sidebar-toggle:hover {
            transform: scale(1.05);
        }
        .annotation-comment {
            margin-bottom: 16px;
            padding: 16px;
            background: var(--card-bg);
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s, transform 0.2s;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
        }
        .annotation-comment:hover {
            background: var(--card-hover);
            transform: translateY(-2px);
        }
        .annotation-comment .quote {
            font-style: italic;
            color: var(--text);
            opacity: 0.7;
            margin-bottom: 8px;
            font-size: 0.9em;
        }
        .annotation-comment .comment {
            font-weight: 700;
            font-size: 1em;
        }
        .annotation-comment .creator {
            font-size: 0.8em;
            color: var(--text);
            opacity: 0.6;
            margin-top: 8px;
        }
        #controls {
            margin-bottom: 24px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }
        #controls button, #controls input, #controls select {
            padding: 8px 16px;
            border-radius: 4px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            background: var(--button-bg);
            color: var(--button-text);
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 700;
            transition: transform 0.2s, background 0.3s;
        }
        #controls button:hover, #controls input:hover, #controls select:hover {
            transform: scale(1.05);
        }
        #user-input {
            background: var(--background);
            color: var(--text);
            border: 1px solid var(--text);
            width: 150px;
        }
        #user-filter {
            width: 200px;
            height: 80px;
            background: var(--background);
            color: var(--text);
        }
        #theme-toggle {
            background: var(--button-bg);
            color: var(--button-text);
        }
        #instructions-overlay {
            position:gevo fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--overlay-bg);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 4;
        }
        #instructions-overlay.hidden {
            display: none;
        }
        #instructions-content {
            background: var(--background);
            padding: 24px;
            border-radius: 8px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            color: var(--text);
        }
        #instructions-content h2 {
            margin-top: 0;
            font-size: 1.5em;
            font-weight: 700;
        }
        #instructions-content p {
            margin: 12px 0;
            line-height: 1.6;
            font-size: 0.9em;
        }
        #instructions-content button {
            background: var(--button-bg);
            color: var(--button-text);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 700;
            transition: transform 0.2s;
        }
        #instructions-content button:hover {
            transform: scale(1.05);
        }
        @media (max-width: 768px) {
            body {
                flex-direction: column;
                padding: 16px;
            }
            #content {
                max-width: 100%;
                margin-bottom: 16px;
            }
            #sidebar {
                position: static;
                width: 100%;
                margin-top: 16px;
                transform: none;
                right: 0;
                top: 0;
            }
            #sidebar.hidden {
                display: none;
            }
            #sidebar-toggle-container {
                position: static;
                margin-bottom: 16px;
            }
            #sidebar-toggle {
                width: 100%;
                border-radius: 4px;
            }
            #instructions-content {
                width: 95%;
                padding: 16px;
            }
            #controls {
                flex-direction: column;
                gap: 8px;
            }
            #user-input, #user-filter {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div id="content">
        <p>Text to annotate. This is a sample paragraph with some content that you can highlight and comment on. Try selecting different parts of this text to add annotations.</p>
        <p>Another paragraph to demonstrate multiple annotations across different sections of the content.</p>
    </div>
    <div id="sidebar-toggle-container">
        <button id="sidebar-toggle">Hide</button>
    </div>
    <div id="sidebar">
        <div id="controls">
            <input type="text" id="user-input" placeholder="Enter your name" value="">
            <select id="user-filter" multiple>
                <option value="">All Users</option>
            </select>
            <button onclick="clearAnnotations()">Clear Annotations</button>
            <button onclick="refreshAnnotations()">Refresh Annotations</button>
            <button onclick="exportAnnotations()">Export Annotations</button>
            <input type="file" id="importAnnotations" accept=".json">
            <button id="theme-toggle">Toggle Theme</button>
            <button id="instructions-button">Show Instructions</button>
        </div>
        <div id="annotation-list"></div>
    </div>
    <div id="instructions-overlay" class="hidden">
        <div id="instructions-content">
            <h2>Annotation Instructions</h2>
            <p><strong>Create Annotations:</strong> Select text in the main content, type a comment, and enter your name in the user input field to save it.</p>
            <p><strong>Highlighting:</strong> When the sidebar is closed, all annotations are highlighted in green. When open, no highlights show unless you toggle one.</p>
            <p><strong>Toggling Highlights:</strong> Click an annotation in the sidebar to show its highlight in the text. Click again to hide it. Only one annotation can be highlighted at a time.</p>
            <p><strong>Other Features:</strong> Use the user filter to view specific users' annotations, refresh to sync changes, clear all annotations, toggle light/dark mode, or export/import them as JSON.</p>
            <button onclick="document.getElementById('instructions-overlay').classList.add('hidden')">Close</button>
        </div>
    </div>
    <script>
        // Initialize RecogitoJS
        const r = Recogito.init({
            content: document.getElementById('content'),
            mode: 'ANNOTATION',
            formatter: (annotation) => {
                return { className: 'r6o-annotation' };
            }
        });

        // State variables
        let currentUser = localStorage.getItem('currentUser') || '';
        let selectedAnnotationId = null;
        let isSidebarVisible = localStorage.getItem('sidebarVisible') !== 'false';
        const userInput = document.getElementById('user-input');
        const sidebar = document.getElementById('sidebar');
        const toggleButton = document.getElementById('sidebar-toggle');
        const content = document.getElementById('content');
        const instructionsButton = document.getElementById('instructions-button');
        const instructionsOverlay = document.getElementById('instructions-overlay');
        const themeToggle = document.getElementById('theme-toggle');
        userInput.value = currentUser;
        updateSidebarVisibility();

        // Theme toggle
        function toggleTheme() {
            const html = document.documentElement;
            const newTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            themeToggle.textContent = newTheme === 'light' ? 'Toggle Dark Mode' : 'Toggle Light Mode';
        }

        // Initialize theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        themeToggle.textContent = savedTheme === 'light' ? 'Toggle Dark Mode' : 'Toggle Light Mode';
        themeToggle.addEventListener('click', toggleTheme);

        // Update currentUser
        userInput.addEventListener('input', () => {
            currentUser = userInput.value.trim();
            localStorage.setItem('currentUser', currentUser);
        });

        // Toggle sidebar
        function toggleSidebar() {
            isSidebarVisible = !isSidebarVisible;
            selectedAnnotationId = null;
            instructionsOverlay.classList.add('hidden');
            localStorage.setItem('sidebarVisible', isSidebarVisible);
            updateSidebarVisibility();
        }

        // Update sidebar visibility and highlights
        function updateSidebarVisibility() {
            if (isSidebarVisible) {
                sidebar.classList.remove('hidden');
                toggleButton.textContent = 'Hide';
                content.classList.add('no-highlights');
                if (selectedAnnotationId) {
                    const activeSpan = document.querySelector(`#content .r6o-annotation[data-id="${selectedAnnotationId}"]`);
                    if (activeSpan) activeSpan.classList.add('active-highlight');
                }
            } else {
                sidebar.classList.add('hidden');
                toggleButton.textContent = 'Annotate';
                content.classList.remove('no-highlights');
                document.querySelectorAll('#content .r6o-annotation.active-highlight').forEach(span => {
                    span.classList.remove('active-highlight');
                });
            }
        }

        // Handle toggle button
        toggleButton.addEventListener('click', toggleSidebar);

        // Handle instructions
        instructionsButton.addEventListener('click', () => {
            instructionsOverlay.classList.remove('hidden');
        });

        // Canonicalize URL
        function getCanonicalPermalink() {
            return window.location.origin + window.location.pathname;
        }

        // Get localStorage key for annotations
        function getLocalStorageKey() {
            return `annotations_${getCanonicalPermalink()}`;
        }

        // Load annotations
        async function loadAnnotations() {
            try {
                const permalink = getCanonicalPermalink();
                let annotations = [];
                
                // Try loading from localStorage first
                const localData = localStorage.getItem(getLocalStorageKey());
                if (localData) {
                    try {
                        annotations = JSON.parse(localData);
                        if (!Array.isArray(annotations)) throw new Error('Invalid localStorage data');
                    } catch (e) {
                        console.warn('Invalid localStorage data, clearing:', e);
                        localStorage.removeItem(getLocalStorageKey());
                    }
                }

                // If localStorage is empty or invalid, fetch from backend
                if (!annotations.length) {
                    const response = await fetch(`/api/annotations/?permalink=${encodeURIComponent(permalink)}`);
                    if (!response.ok) throw new Error('Failed to load annotations from server');
                    annotations = await response.json();
                    localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
                }

                r.setAnnotations(annotations);
                updateSidebar(annotations);
                updateUserFilter(annotations);
                console.log('Loaded annotations:', annotations);
            } catch (error) {
                console.error('Error loading annotations:', error);
                alert('Failed to load annotations from server. Using local annotations if available.');
            }
        }

        // Save annotation
        async function saveAnnotation(annotation) {
            try {
                const permalink = getCanonicalPermalink();
                const version = new Date().toISOString();
                const updatedAnnotation = {
                    ...annotation,
                    creator: {
                        type: 'Person',
                        name: currentUser || 'Anonymous'
                    },
                    version: version
                };

                // Save to backend
                const response = await fetch('/api/annotations/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user: currentUser, permalink, annotation: updatedAnnotation })
                });

                let annotations;
                if (!response.ok) {
                    const error = await response.json();
                    if (error.detail.includes('conflict')) {
                        alert('Annotation was updated by another user. Please refresh.');
                        return;
                    }
                    throw new Error('Failed to save annotation to server');
                } else {
                    // Fetch updated annotations from backend
                    annotations = await fetchAnnotations();
                }

                // Update localStorage
                localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
                updateSidebar(annotations);
                updateUserFilter(annotations);
                console.log('Annotation saved:', updatedAnnotation);
            } catch (error) {
                console.error('Error saving annotation:', error);
                // Save to localStorage as fallback
                let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
                const existingIndex = annotations.findIndex(a => a.id === updatedAnnotation.id);
                if (existingIndex >= 0) {
                    annotations[existingIndex] = updatedAnnotation;
                } else {
                    annotations.push(updatedAnnotation);
                }
                localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
                r.setAnnotations(annotations);
                updateSidebar(annotations);
                updateUserFilter(annotations);
                alert('Failed to save annotation to server. Saved locally.');
            }
        }

        // Fetch annotations from backend
        async function fetchAnnotations() {
            const permalink = getCanonicalPermalink();
            const response = await fetch(`/api/annotations/?permalink=${encodeURIComponent(permalink)}`);
            if (!response.ok) throw new Error('Failed to fetch annotations');
            return await response.json();
        }

        // Update user filter
        function updateUserFilter(annotations) {
            const userFilter = document.getElementById('user-filter');
            const creators = [...new Set(annotations.map(a => a.creator?.name || 'Unknown'))];
            const allUsersOption = '<option value="">All Users</option>';
            const options = creators.map(creator => `<option value="${creator}">${creator}</option>`).join('');
            userFilter.innerHTML = allUsersOption + options;
        }

        // Update sidebar
        function updateSidebar(annotations) {
            const list = document.getElementById('annotation-list');
            const userFilter = document.getElementById('user-filter');
            const selectedUsers = Array.from(userFilter.selectedOptions).map(option => option.value);
            const filteredAnnotations = selectedUsers.length === 0 || selectedUsers.includes('')
                ? annotations
                : annotations.filter(a => selectedUsers.includes(a.creator?.name || 'Unknown'));
            list.innerHTML = '';
            filteredAnnotations.forEach(annotation => {
                const comment = annotation.body?.find(b => b.purpose === 'commenting')?.value || 'No comment';
                const quote = annotation.target?.selector?.find(s => s.type === 'TextQuoteSelector')?.exact || 'No quote';
                const creator = annotation.creator?.name || 'Unknown';
                const div = document.createElement('div');
                div.className = 'annotation-comment';
                div.dataset.annotationId = annotation.id;
                div.innerHTML = `
                    <div class="quote">${quote}</div>
                    <div class="comment">${comment}</div>
                    <div class="creator">By: ${creator}</div>
                `;
                const position = getAnnotationPosition(annotation);
                div.style.marginTop = `${position}px`;
                div.addEventListener('click', () => {
                    if (isSidebarVisible) {
                        selectedAnnotationId = selectedAnnotationId === annotation.id ? null : annotation.id;
                        document.querySelectorAll('#content .r6o-annotation.active-highlight').forEach(span => {
                            span.classList.remove('active-highlight');
                        });
                        if (selectedAnnotationId) {
                            const activeSpan = document.querySelector(`#content .r6o-annotation[data-id="${selectedAnnotationId}"]`);
                            if (activeSpan) activeSpan.classList.add('active-highlight');
                        }
                    }
                });
                list.appendChild(div);
            });
        }

        // Estimate annotation position
        function getAnnotationPosition(annotation) {
            const selector = annotation.target?.selector?.find(s => s.type === 'TextPositionSelector');
            if (selector && selector.start != null) {
                const range = document.createRange();
                const content = document.getElementById('content');
                let charCount = 0;
                let found = false;
                for (let node of content.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        if (charCount + node.length >= selector.start) {
                            range.setStart(node, selector.start - charCount);
                            range.setEnd(node, selector.start - charCount);
                            found = true;
                            break;
                        }
                        charCount += node.length;
                    }
                }
                if (found) {
                    const rect = range.getBoundingClientRect();
                    const contentRect = content.getBoundingClientRect();
                    return rect.top - contentRect.top + content.scrollTop;
                }
            }
            return 0;
        }

        // Clear annotations
        async function clearAnnotations() {
            try {
                const permalink = getCanonicalPermalink();
                const response = await fetch(`/api/annotations/?permalink=${encodeURIComponent(permalink)}`, {
                    method: 'DELETE'
                });
                if (!response.ok) throw new Error('Failed to clear annotations from server');
                r.setAnnotations([]);
                const highlights = document.querySelectorAll('#content .r6o-annotation');
                highlights.forEach(span => {
                    const parent = span.parentNode;
                    while (span.firstChild) {
                        parent.insertBefore(span.firstChild, span);
                    }
                    parent.removeChild(span);
                });
                selectedAnnotationId = null;
                instructionsOverlay.classList.add('hidden');
                localStorage.removeItem(getLocalStorageKey());
                updateSidebar([]);
                updateUserFilter([]);
                console.log('Annotations cleared');
            } catch (error) {
                console.error('Error clearing annotations:', error);
                // Clear localStorage as fallback
                localStorage.removeItem(getLocalStorageKey());
                r.setAnnotations([]);
                updateSidebar([]);
                updateUserFilter([]);
                alert('Failed to clear annotations from server. Cleared locally.');
            }
        }

        // Refresh annotations
        async function refreshAnnotations() {
            try {
                const annotations = await fetchAnnotations();
                localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
                r.setAnnotations(annotations);
                updateSidebar(annotations);
                updateUserFilter(annotations);
                console.log('Annotations refreshed');
            } catch (error) {
                console.error('Error refreshing annotations:', error);
                alert('Failed to refresh annotations from server. Using local annotations.');
            }
        }

        // Export annotations
        async function exportAnnotations() {
            try {
                let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
                if (!annotations.length) {
                    annotations = await fetchAnnotations();
                }
                const blob = new Blob([JSON.stringify(annotations)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'annotations.json';
                a.click();
                URL.revokeObjectURL(url);
                console.log('Annotations exported');
            } catch (error) {
                console.error('Error exporting annotations:', error);
                alert('Failed to export annotations.');
            }
        }

        // Import annotations
        document.getElementById('importAnnotations').addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = async (e) => {
                    try {
                        const annotations = JSON.parse(e.target.result);
                        const permalink = getCanonicalPermalink();
                        let localAnnotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
                        for (const annotation of annotations) {
                            const version = new Date().toISOString();
                            const updatedAnnotation = { ...annotation, version };
                            const response = await fetch('/api/annotations/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ user: currentUser, permalink, annotation: updatedAnnotation })
                            });
                            if (response.ok) {
                                const existingIndex = localAnnotations.findIndex(a => a.id === updatedAnnotation.id);
                                if (existingIndex >= 0) {
                                    localAnnotations[existingIndex] = updatedAnnotation;
                                } else {
                                    localAnnotations.push(updatedAnnotation);
                                }
                            }
                        }
                        localStorage.setItem(getLocalStorageKey(), JSON.stringify(localAnnotations));
                        r.setAnnotations(localAnnotations);
                        selectedAnnotationId = null;
                        updateSidebar(localAnnotations);
                        updateUserFilter(localAnnotations);
                        console.log('Imported annotations:', annotations);
                    } catch (error) {
                        console.error('Error importing annotations:', error);
                        alert('Failed to import annotations to server. Saved locally.');
                    }
                };
                reader.readAsText(file);
            }
        });

        // Handle filter changes
        document.getElementById('user-filter').addEventListener('change', async () => {
            let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
            if (!annotations.length) {
                annotations = await fetchAnnotations();
            }
            updateSidebar(annotations);
        });

        // Handle annotation events
        r.on('createAnnotation', saveAnnotation);
        r.on('updateAnnotation', saveAnnotation);
        r.on('deleteAnnotation', async (annotation) => {
            try {
                const permalink = getCanonicalPermalink();
                const response = await fetch(`/api/annotations/${annotation.id}/`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user: currentUser, permalink })
                });
                if (!response.ok) throw new Error('Failed to delete annotation from server');
                let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
                annotations = annotations.filter(a => a.id !== annotation.id);
                localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
                updateSidebar(annotations);
                updateUserFilter(annotations);
                if (selectedAnnotationId === annotation.id) {
                    selectedAnnotationId = null;
                }
                console.log('Annotation deleted:', annotation);
            } catch (error) {
                console.error('Error deleting annotation:', error);
                // Update localStorage as fallback
                let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
                annotations = annotations.filter(a => a.id !== annotation.id);
                localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
                updateSidebar(annotations);
                updateUserFilter(annotations);
                alert('Failed to delete annotation from server. Deleted locally.');
            }
        });

        // Initialize
        loadAnnotations();
    </script>
</body>
</html>
```

**Notes**:

- Identical to April 27, 2025, version.
- Uses `localStorage` (`annotations_<permalink>`) and `/api/annotations/`.
- MkDocs Material styling, Nunito Sans, green highlights, “Annotate”/“Hide”.

---

### Additional Django Files

To complete the Django app, here are the remaining files (unchanged from April 26, 2025, but included for completeness).
These are assumed to exist in `annotations/` and `project/`.

#### `annotations/models.py`

```python
from django.db import models


class Annotation(models.Model):
    user = models.CharField(max_length=255)
    permalink = models.TextField()
    annotation = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['permalink']),
        ]
```

#### `annotations/serializers.py`

```python
from rest_framework import serializers
from .models import Annotation


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['id', 'user', 'permalink', 'annotation', 'timestamp']
```

#### `annotations/views.py`

```python
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Annotation
from .serializers import AnnotationSerializer


class AnnotationListCreate(generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer

    def get_queryset(self):
        permalink = self.request.query_params.get('permalink')
        if permalink:
            return Annotation.objects.filter(permalink=permalink)
        return Annotation.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AnnotationDelete(generics.DestroyAPIView):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnnotationDeleteByPermalink(generics.GenericAPIView):
    def delete(self, request, *args, **kwargs):
        permalink = request.query_params.get('permalink')
        if not permalink:
            return Response({'detail': 'Permalink is required'}, status=status.HTTP_400_BAD_REQUEST)
        Annotation.objects.filter(permalink=permalink).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### `annotations/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('annotations/', views.AnnotationListCreate.as_view(), name='annotation-list-create'),
    path('annotations/<int:pk>/', views.AnnotationDelete.as_view(), name='annotation-delete'),
    path('annotations/delete_by_permalink/', views.AnnotationDeleteByPermalink.as_view(),
         name='annotation-delete-by-permalink'),
]
```

#### `project/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('annotations.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]
```

**Notes**:

- `annotations/` handles API logic (CRUD for `Annotation` model).
- `project/urls.py` serves `index.html` at `/` and routes `/api/annotations/`.

---

### Setup Instructions

1. **Create Project Directory**:
   ```
   mkdir project
   cd project
   ```

2. **Save Artifacts**:
    - Place files in the structure above:
        - `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `schema.sql`, `nginx.conf` in `project/`.
        - `index.html` in `project/static/`.
        - `settings.py`, `urls.py` in `project/project/`.
        - `models.py`, `serializers.py`, `views.py`, `urls.py` in `project/annotations/`.
    - Create empty `annotations/__init__.py`, `project/__init__.py`, `project/asgi.py`, `project/wsgi.py`.
    - Create `annotations/migrations/` with empty `__init__.py`.

3. **Update `DJANGO_SECRET_KEY`**:
    - In `docker-compose.yml`, replace `your-secret-key-change-me` with a secure key:
      ```bash
      python -c "import secrets; print(secrets.token_urlsafe(50))"
      ```
    - Or set via environment variable in `.env`:
      ```
      DJANGO_SECRET_KEY=your-secure-key
      ```

4. **Run Docker Compose**:
   ```bash
   docker-compose up --build
   ```
    - Builds and starts `db` and `app`.
    - PostgreSQL initializes with `schema.sql`.
    - Django runs migrations, collects static files, and starts Gunicorn.
    - Access: `http://localhost:8000`.

5. **Verify Setup**:
    - **Frontend**:
        - Open `http://localhost:8000`.
        - Confirm `index.html` loads (MkDocs Material, Nunito Sans, “Annotate” button).
    - **Database**:
        - Connect to PostgreSQL:
          ```bash
          docker exec -it <db-container> psql -U annotations_user -d annotations_db
          ```
        - Verify table:
          ```sql
          \dt
          SELECT * FROM annotations;
          ```
    - **APIs**:
        - Test `/api/annotations/`:
          ```bash
          curl http://localhost:8000/api/annotations/
          ```
        - Should return `[]` (empty initially).

6. **Test Annotations**:
    - **Create**:
        - Enter “Alice” in `#user-input`.
        - Highlight text, add comment, save.
        - Check `localStorage` (DevTools > Application > Local Storage >
          `annotations_http://localhost:8000/index.html`).
        - Verify PostgreSQL:
          ```sql
          SELECT * FROM annotations;
          ```
    - **Offline**:
        - Go offline (DevTools > Network > Offline).
        - Create annotation; confirm `localStorage` update, see “Saved locally” alert.
        - Reload; verify annotations load from `localStorage`.
    - **Clear**:
        - Click “Clear Annotations”.
        - Confirm `localStorage` key and PostgreSQL table cleared.
    - **Other Features**:
        - Test sidebar (“Annotate”/“Hide”), green highlights (`#4caf50`), user filter, instructions, export/import,
          theme toggle.
        - Test multi-page (copy `index.html` to `static/about.html`, access `http://localhost:8000/about.html`).

---

### Kubernetes Guidance

To deploy in Kubernetes, convert the Docker Compose setup to manifests. Here’s a basic example:

1. **PostgreSQL Deployment**:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: annotations-db
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: annotations-db
     template:
       metadata:
         labels:
           app: annotations-db
       spec:
         containers:
         - name: postgres
           image: postgres:15
           env:
           - name: POSTGRES_DB
             value: annotations_db
           - name: POSTGRES_USER
             value: annotations_user
           - name: POSTGRES_PASSWORD
             value: annotations_pass
           volumeMounts:
           - name: postgres-data
             mountPath: /var/lib/postgresql/data
           - name: init-sql
             mountPath: /docker-entrypoint-initdb.d
         volumes:
         - name: postgres-data
           persistentVolumeClaim:
             claimName: postgres-pvc
         - name: init-sql
           configMap:
             name: annotations-init-sql
   ---
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: postgres-pvc
   spec:
     accessModes:
     - ReadWriteOnce
     storageClassName: standard
     resources:
       requests:
         storage: 1Gi
   ---
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: annotations-init-sql
   data:
     schema.sql: |
       CREATE TABLE annotations (
           id SERIAL PRIMARY KEY,
           user VARCHAR(255) NOT NULL,
           permalink TEXT NOT NULL,
           annotation JSONB NOT NULL,
           timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
       );
       CREATE INDEX idx_annotations_permalink ON annotations (permalink);
   ```

2. **Django Deployment**:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: annotations-app
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: annotations-app
     template:
       metadata:
         labels:
           app: annotations-app
       spec:
         containers:
         - name: app
           image: annotations-app:latest
           env:
           - name: DATABASE_URL
             value: postgresql://annotations_user:annotations_pass@annotations-db:5432/annotations_db
           - name: DJANGO_SECRET_KEY
             value: your-secret-key-change-me
           - name: DEBUG
             value: "True"
           ports:
           - containerPort: 8000
           volumeMounts:
           - name: static
             mountPath: /app/static
         volumes:
         - name: static
           emptyDir: {}
   ```

3. **Services**:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: annotations-db
   spec:
     selector:
       app: annotations-db
     ports:
     - port: 5432
       targetPort: 5432
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: annotations-app
   spec:
     selector:
       app: annotations-app
     ports:
     - port: 80
       targetPort: 8000
     type: ClusterIP
   ```

4. **Ingress** (Optional):
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: annotations-ingress
   spec:
     rules:
     - host: annotations.local
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: annotations-app
               port:
                 number: 80
   ```

5. **Steps**:
    - Build and push Docker image:
      ```bash
      docker build -t annotations-app:latest .
      docker push annotations-app:latest  # To your registry
      ```
    - Apply manifests:
      ```bash
      kubectl apply -f postgres.yaml -f app.yaml -f services.yaml -f ingress.yaml
      ```
    - Configure DNS (e.g., `annotations.local` in `/etc/hosts`).
    - Use `minikube` or a local cluster for testing.

**Notes**:

- Replace `annotations-app:latest` with your registry (e.g., Docker Hub, private registry).
- Use a `Secret` for `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`.
- Configure `storageClassName` based on your cluster (e.g., `standard`, `local-path`).
- Add `livenessProbe`/`readinessProbe` for production.

---

### Testing Instructions

1. **Local Testing**:
    - Run `docker-compose up --build`.
    - Access `http://localhost:8000`.
    - Test annotations:
        - Create as “Alice”; verify `localStorage` and PostgreSQL.
        - Go offline; create annotation; confirm `localStorage` update.
        - Clear, refresh, export/import, toggle sidebar, filter users.
    - Check logs:
      ```bash
      docker logs <app-container>
      docker logs <db-container>
      ```

2. **Feature Testing**:
    - **Sidebar**: “Annotate” (hidden), “Hide” (visible); green highlights (`#4caf50`).
    - **Filter**: Select users; verify sidebar updates.
    - **Theme**: Toggle light/dark; check `localStorage` (`theme`).
    - **Multi-Page**: Copy `index.html` to `static/about.html`; verify separate `localStorage` and PostgreSQL rows.
    - **Concurrency**: Open two browsers; test conflict alerts.

3. **Database Testing**:
    - Query:
      ```sql
      SELECT * FROM annotations;
      ```
    - Verify `permalink`, `user`, `annotation->>'version'`.

4. **Kubernetes Testing**:
    - Deploy manifests to a local cluster (e.g., `minikube`).
    - Access via `Ingress` or `kubectl port-forward`.
    - Repeat annotation tests.

---

### Troubleshooting

- **Django Not Connecting to PostgreSQL**:
    - Check `DATABASE_URL` or `DATABASES` settings.
    - Verify `db` service is healthy:
      ```bash
      docker exec -it <db-container> pg_isready
      ```
- **Annotations Not Saving**:
    - Check Console for `fetch` errors.
    - Verify `localStorage` (`annotations_<permalink>`).
    - Test API:
      ```bash
      curl -X POST http://localhost:8000/api/annotations/ -d '{"user":"Alice","permalink":"http://localhost:8000/index.html","annotation":{"id":"test","version":"2025-04-27T00:00:00Z"}}' -H "Content-Type: application/json"
      ```
- **Static Files Not Loading**:
    - Run `python manage.py collectstatic`.
    - Check `STATIC_ROOT` (`staticfiles/`).
- **Kubernetes Issues**:
    - Verify `PersistentVolumeClaim` binding.
    - Check pod logs:
      ```bash
      kubectl logs -l app=annotations-app
      ```

---

### Limitations and Notes

- **Storage**: Kept PostgreSQL JSONB and `localStorage`. If you want a different database (e.g., MongoDB) or
  `localStorage`-only, I’ll redesign.
- **Nginx**: Excluded from `docker-compose.yml` for simplicity; enable for Kubernetes or production.
- **Kubernetes**: Provided basic manifests; Helm chart or advanced configs available on request.
- **Security**: `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD` are hardcoded for demo; use `Secret` or `.env` in
  production.
- **No AWS**: Setup is cloud-agnostic, works with any Kubernetes cluster or local Docker.

---

### Enhancements (Optional)

- **Storage Alternatives**:
    - Replace PostgreSQL with SQLite (simpler for local) or MongoDB (JSON-native).
    - Remove `localStorage`, rely solely on backend.
- **UI Feedback**:
    - Add toast for “Saved locally”/“Synced” (as suggested April 27, 2025).
    - Change “Hide” to “Close”.
- **Backend**:
    - Add `PATCH /api/annotations/<id>/` for partial updates.
    - Implement auto-refresh (`setInterval`).
- **Kubernetes**:
    - Provide Helm chart.
    - Add `HorizontalPodAutoscaler`.
- **Okta**: Integrate SAML for `currentUser`.

---

### Final Notes

- **Storage**: Maintained PostgreSQL JSONB (`annotations` table) and `localStorage` (`annotations_<permalink>`).
- **Docker Compose**: Set up `db` (PostgreSQL) and `app` (Django) services; optional `nginx`.
- **Kubernetes**: Provided manifests for deployment.
- **Frontend**: Kept `index.html` with all features (RecogitoJS, MkDocs Material, Nunito Sans, green highlights,
  “Annotate”/“Hide”).
- **No AWS**: Cloud-agnostic, portable setup.

Please:

- **Test the setup**: Run `docker-compose up` and verify annotations save (localStorage, PostgreSQL).
- **Clarify storage**: Confirm if PostgreSQL JSONB + `localStorage` is correct or specify changes (e.g., MongoDB,
  `localStorage`-only).
- **Specify next steps**: Any enhancements (e.g., toast, Kubernetes Helm, Okta)?
- **Report issues**: Share errors, logs, or unexpected behavior.

I’m ready to iterate! Let me know your feedback or additional requirements.