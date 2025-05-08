The Django template loading error you’re encountering indicates that Django’s template loader (
`django.template.loaders.app_directories.Loader`) is failing to find the `index.html` template in the expected locations
for installed apps (`django.contrib.admin`, `django.contrib.auth`, `rest_framework`). The error message shows it’s
looking for `index.html` directly under the app’s `templates/` directory (e.g.,
`/usr/local/lib/python3.11/site-packages/django/contrib/admin/templates/index.html`), but the actual file for `admin`
exists at a deeper path (`/usr/local/lib/python3.11/site-packages/django/contrib/admin/templates/admin/index.html`).
This suggests a misconfiguration in how Django is resolving templates, likely related to the `TEMPLATES` setting or
static file handling in your project.

Given your project setup (Django 4.2.11, SQLite, Gunicorn, Docker Compose, with `index.html` in `static/` served via
`TemplateView`), let’s diagnose the issue, identify the root cause, and provide a fix. I’ll also address whether this
could be a Django version issue or a settings misconfiguration, ensuring alignment with the project structure from our
previous discussions (April 28, 2025).

---

### Understanding the Error

The error occurs when Django tries to load the `index.html` template, as specified in your `project/urls.py`:

```python
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('annotations.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]
```

The `TemplateView` is configured to render `index.html`, but Django’s template loader is searching in the wrong
directories. The error messages indicate:

1. **Incorrect Template Paths**:
    - Django is looking for `index.html` in:
        - `/usr/local/lib/python3.11/site-packages/django/contrib/admin/templates/index.html`
        - `/usr/local/lib/python3.11/site-packages/django/contrib/auth/templates/index.html`
        - `/usr/local/lib/python3.11/site-packages/rest_framework/templates/index.html`
    - However, the actual `admin` template is at
      `/usr/local/lib/python3.11/site-packages/django/contrib/admin/templates/admin/index.html`, suggesting Django
      expects templates at the root of each app’s `templates/` directory, not in subdirectories like `templates/admin/`.

2. **Your `index.html`**:
    - Your `index.html` is in `static/index.html`, intended to be served as a static file but rendered via
      `TemplateView`.
    - Django’s template loader isn’t finding `static/index.html` because `static/` is not a template directory by
      default; it’s for static assets (CSS, JS, etc.).

3. **Template Loader Behavior**:
    - The `app_directories.Loader` searches for templates in the `templates/` directory of each app listed in
      `INSTALLED_APPS`:
      ```python
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
      ```
    - It’s checking `templates/index.html` in each app but not finding it, and it’s not looking in `static/` or a custom
      template directory.

---

### Possible Causes

Based on the project setup and error, here are the likely causes:

1. **Misconfigured `TEMPLATES` Setting**:
    - Your `settings.py` defines the `TEMPLATES` setting as:
      ```python
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
      ```
    - **`DIRS': []`**: No custom template directories are specified, so Django only looks in app-specific `templates/`
      directories (e.g., `annotations/templates/`).
    - **`APP_DIRS': True`**: Enables `app_directories.Loader`, which searches `templates/` in each `INSTALLED_APPS` app.
    - **Issue**: Django isn’t configured to look in `static/` for templates, and `static/index.html` isn’t in a
      `templates/` directory. The loader is also mistakenly expecting `index.html` at the root of app template
      directories (e.g., `admin/templates/index.html` instead of `admin/templates/admin/index.html`).

2. **Static vs. Template File**:
    - Your `index.html` is in `static/`, typically used for static assets (served via `STATIC_URL` and `collectstatic`).
    - `TemplateView` expects `index.html` to be in a template directory (e.g., `templates/index.html` or
      `annotations/templates/index.html`).
    - **Issue**: Placing `index.html` in `static/` and expecting `TemplateView` to render it causes a mismatch, as
      `static/` is not scanned by the template loader.

3. **Docker Volume Mapping**:
    - The `docker-compose.yml` maps `./static:/app/static`:
      ```yaml
      volumes:
        - ./static:/app/static
        - ./annotations:/app/annotations
        - ./project:/app/project
        - ./annotations.db:/app/annotations.db
      ```
    - If `static/index.html` exists on the host but isn’t correctly mapped or accessible in the container, Django won’t
      find it.
    - **Issue**: The template loader doesn’t look in `/app/static` unless explicitly configured.

4. **Django Version Issue**:
    - You’re using Django 4.2.11 (`requirements.txt`):
      ```text
      django==4.2.11
      djangorestframework==3.15.1
      gunicorn==22.0.0
      ```
    - Django 4.2.11 is a stable LTS release, and its template loading behavior is consistent with prior versions. The
      `app_directories.Loader` should correctly find app templates (e.g., `admin/templates/admin/index.html`).
    - **Unlikely Issue**: The error suggests a configuration issue rather than a version bug, as Django 4.2.11 handles
      templates correctly when configured properly. However, the loader’s expectation of `templates/index.html` instead
      of `templates/admin/index.html` could indicate a subtle misconfiguration or override.

5. **Template Directory Structure**:
    - The `admin` app has templates in `templates/admin/`, but the loader is looking for `templates/index.html`.
    - This could be caused by:
        - A custom template loader or middleware interfering with the default behavior.
        - An incorrect assumption by `TemplateView` that `index.html` exists at the root of app template directories.
    - **Issue**: The project expects `index.html` to be served from `static/`, not an app’s `templates/` directory.

---

### Fix: Correct Template Configuration

To resolve the issue, we need to ensure Django’s template loader can find `index.html`. Since `index.html` is in
`static/` but used as a template, we’ll move it to a proper template directory and update the configuration. Here’s the
step-by-step fix:

#### 1. Move `index.html` to a Template Directory

- **Action**: Move `static/index.html` to `templates/index.html` (create a `templates/` directory in the project root).
- **Reason**: `TemplateView` expects templates in directories specified by `TEMPLATES['DIRS']` or app `templates/`
  directories, not `static/`.

**Steps**:

```bash
cd project
mkdir templates
mv static/index.html templates/index.html
```

#### 2. Update `settings.py` to Include `templates/` Directory

- **Action**: Add the `templates/` directory to `TEMPLATES['DIRS']` in `settings.py`.
- **Reason**: This tells Django’s template loader to look in `project/templates/` for templates like `index.html`.

**Updated `settings.py`**:

```python
import os
from pathlib import Path

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
        'DIRS': [BASE_DIR / 'templates'],  # Add templates/ directory
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'annotations.db',
    }
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

**Changes**:

- Added `'DIRS': [BASE_DIR / 'templates']` to include `project/templates/`.
- Kept `APP_DIRS: True` to allow app-specific templates (e.g., `annotations/templates/` if needed).

#### 3. Update `docker-compose.yml` Volume

- **Action**: Add a volume mapping for `templates/` to ensure the container sees `templates/index.html`.
- **Reason**: The Docker container needs access to the new `templates/` directory.

**Updated `docker-compose.yml`**:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DJANGO_SECRET_KEY=your-secret-key-change-me
      - DEBUG=True
    volumes:
      - ./static:/app/static
      - ./templates:/app/templates  # Add templates volume
      - ./annotations:/app/annotations
      - ./project:/app/project
      - ./annotations.db:/app/annotations.db
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --worker-class sync --bind 0.0.0.0:8000 project.wsgi:application"
    ports:
      - "8000:8000"
```

**Changes**:

- Added `- ./templates:/app/templates` to map the `templates/` directory.
- Kept `--worker-class sync` to ensure WSGI (from previous fix).

#### 4. Remove or Empty `static/` Directory

- **Action**: Since `index.html` is now in `templates/`, you can remove `static/index.html` or leave `static/` empty.
- **Reason**: `static/` is for static assets (CSS, JS), not templates. `collectstatic` will still work with an empty
  `static/`.

**Steps**:

```bash
rm -rf static/index.html
# Or keep static/ empty:
mkdir -p static
```

#### 5. Rebuild and Run

- **Action**: Rebuild the Docker image and restart the container to apply changes.
- **Steps**:

```bash
cd project
docker-compose down -v
docker-compose up --build
```

#### 6. Verify Template Loading

- **Action**: Test the application to ensure `index.html` loads.
- **Steps**:
    - Access `http://localhost:8000`.
    - Confirm the annotation interface (RecogitoJS, “Annotate”/“Close” button) appears.
    - Check Docker logs for errors:
      ```bash
      docker ps  # Find container name
      docker logs <app-container>
      ```
    - If errors persist, check the container’s file system:
      ```bash
      docker exec -it <app-container> bash
      ls -l /app/templates/
      ```
        - Ensure `/app/templates/index.html` exists.

#### 7. Test Admin and APIs

- **Action**: Verify other routes to ensure no template issues.
- **Steps**:
    - Admin: `http://localhost:8000/admin/` (should load `admin/index.html` correctly).
    - API: `curl http://localhost:8000/api/annotations/`.
    - Annotations: Create an annotation at `http://localhost:8000` and verify SQLite:
      ```bash
      sqlite3 annotations.db "SELECT * FROM annotations_annotation;"
      ```

---

### Alternative: Keep `index.html` in `static/` (Not Recommended)

If you prefer to keep `index.html` in `static/` (e.g., for consistency with static asset workflows), you can configure
Django to treat `static/` as a template directory, but this is unconventional and may cause issues with `collectstatic`.

**Steps (Not Recommended)**:

1. Update `settings.py`:
   ```python
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [BASE_DIR / 'static'],  # Use static/ as template dir
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [...],
           },
       },
   ]
   ```
2. Ensure `static/index.html` is not collected to `staticfiles/`:
    - Modify `docker-compose.yml` to skip `collectstatic` or exclude `index.html`:
      ```yaml
      command: >
        sh -c "python manage.py migrate &&
               gunicorn --worker-class sync --bind 0.0.0.0:8000 project.wsgi:application"
      ```
3. Rebuild:
   ```bash
   docker-compose up --build
   ```

**Why Avoid This**:

- `static/` is for assets served via `STATIC_URL`, not templates.
- `collectstatic` may copy `index.html` to `staticfiles/`, causing confusion.
- Mixing template and static file roles violates Django conventions.

---

### Addressing Django Version Concerns

**Is This a Django 4.2.11 Issue?**

- **Unlikely**: Django 4.2.11 is a stable LTS release, and its template loading (`app_directories.Loader`) is
  well-tested. The loader correctly finds app templates (e.g., `admin/templates/admin/index.html`) when configured
  properly.
- **Evidence**: The error shows the loader checking app `templates/` directories, but it’s looking for `index.html` at
  the root (`templates/index.html`) instead of subdirectories (`templates/admin/index.html`). This is expected behavior
  when `TemplateView` specifies `index.html`, and no such file exists in the app’s `templates/` root.
- **Conclusion**: The issue is a configuration mismatch (wrong template location), not a Django bug.

**Why the Loader Expects `templates/index.html`**?

- `TemplateView.as_view(template_name='index.html')` tells Django to find `index.html` in:
    - `TEMPLATES['DIRS']` (empty, so skipped).
    - Each app’s `templates/` directory (e.g., `admin/templates/`, `auth/templates/`).
- Since `index.html` was in `static/`, and no app has `templates/index.html`, the loader fails.

---

### Troubleshooting If the Fix Doesn’t Work

If the error persists after applying the fix:

1. **Check Template File**:
    - Verify `templates/index.html` exists:
      ```bash
      ls -l project/templates/
      ```
    - In the container:
      ```bash
      docker exec -it <app-container> ls -l /app/templates/
      ```

2. **Inspect Logs**:
    - Check for additional errors:
      ```bash
      docker logs <app-container>
      ```
    - Look for template loading or file access issues.

3. **Test with Debug**:
    - Ensure `DEBUG = True` in `settings.py` to get detailed error pages.
    - Access `http://localhost:8000` and check the error page for template paths.

4. **Verify `urls.py`**:
    - Confirm `TemplateView` is correct:
      ```python
      path('', TemplateView.as_view(template_name='index.html'), name='index'),
      ```

5. **Check App Templates**:
    - If Django still looks for `admin/templates/index.html`, it’s because `APP_DIRS: True` is enabled.
    - Temporarily disable `APP_DIRS` to isolate:
      ```python
      TEMPLATES = [
          {
              'BACKEND': 'django.template.backends.django.DjangoTemplates',
              'DIRS': [BASE_DIR / 'templates'],
              'APP_DIRS': False,  # Disable app directories
              'OPTIONS': {
                  'context_processors': [...],
              },
          },
      ]
      ```
    - Rebuild and test. Note: This will break `admin/` unless `admin/templates/` is copied to `project/templates/`.

6. **Clear Docker Cache**:
    - Ensure no stale images or volumes:
      ```bash
      docker-compose down -v
      docker system prune -f
      docker-compose up --build
      ```

7. **Test Admin Templates**:
    - Access `http://localhost:8000/admin/` to confirm `admin/templates/admin/index.html` loads.
    - If it fails, check the container’s Python site-packages:
      ```bash
      docker exec -it <app-container> ls -l /usr/local/lib/python3.11/site-packages/django/contrib/admin/templates/admin/
      ```

---

### Updated Artifacts

Below are the updated files reflecting the fix. Replace these in your project.

#### 1. `settings.py`

```python
import os
from pathlib import Path

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
        'DIRS': [BASE_DIR / 'templates'],
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'annotations.db',
    }
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

#### 2. `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DJANGO_SECRET_KEY=your-secret-key-change-me
      - DEBUG=True
    volumes:
      - ./static:/app/static
      - ./templates:/app/templates
      - ./annotations:/app/annotations
      - ./project:/app/project
      - ./annotations.db:/app/annotations.db
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --worker-class sync --bind 0.0.0.0:8000 project.wsgi:application"
    ports:
      - "8000:8000"
```

---

### Summary

**Cause**:

- Django’s template loader couldn’t find `index.html` because it was in `static/` (not a template directory) and not in
  `templates/` or an app’s `templates/` directory.
- The `TEMPLATES['DIRS']` setting was empty, so Django only searched app `templates/` directories (e.g.,
  `admin/templates/`), expecting `index.html` at the root.

**Fix**:

- Moved `index.html` to `templates/index.html`.
- Updated `settings.py` to include `BASE_DIR / 'templates'` in `TEMPLATES['DIRS']`.
- Added `templates/` volume to `docker-compose.yml`.
- Removed `static/index.html` to avoid confusion.

**Django Version**:

- Django 4.2.11 is not the issue; the problem was a configuration mismatch.

**Next Steps**:

- Apply the updated `settings.py` and `docker-compose.yml`.
- Move `index.html` to `templates/`.
- Rebuild and test: `docker-compose down -v && docker-compose up --build`.
- Verify `http://localhost:8000` and `http://localhost:8000/admin/`.
- Share logs or errors if the issue persists.

Let me know the results or if you need further assistance!