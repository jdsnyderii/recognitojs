The error `ASGIHandler.__call__() missing 1 required positional argument: 'send'` typically occurs in a Django
application when there’s a mismatch or misconfiguration related to the ASGI (Asynchronous Server Gateway Interface)
setup. This error suggests that the ASGI handler (likely `django.core.asgi.ASGIHandler`) is being invoked incorrectly,
specifically missing the `send` argument required for handling asynchronous HTTP responses. Since your project uses
Django with Gunicorn (as specified in the `Dockerfile` and `docker-compose.yml`), this issue likely stems from how the
application is being run or configured.

Let’s break down the cause, identify potential issues in your setup, and provide a fix. I’ll also ensure the solution
aligns with the project structure and requirements from our previous discussion (April 28, 2025), which uses Django
4.2.11, SQLite, and Gunicorn in a Docker Compose environment.

---

### Why the `send` Argument is Missing

The `ASGIHandler.__call__` method in Django’s `django.core.asgi` module is defined as:

```python
async def __call__(self, scope, receive, send):
    ...
```

It expects three arguments:

- `scope`: A dictionary containing details about the incoming request (e.g., HTTP method, path).
- `receive`: An awaitable for receiving incoming messages (e.g., request body).
- `send`: An awaitable for sending responses (e.g., HTTP response).

The error indicates that `send` is not being provided when `ASGIHandler` is called, which typically happens in one of
these scenarios:

1. **Running an ASGI Application with a WSGI Server**:
    - Your `Dockerfile` and `docker-compose.yml` specify Gunicorn with `project.wsgi:application`:
      ```dockerfile
      CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project.wsgi:application"]
      ```
    - Gunicorn is a **WSGI** server, designed to work with Django’s WSGI application (`project.wsgi:application`).
    - However, if the `project.asgi:application` (ASGI) is mistakenly used or referenced, or if Gunicorn is
      misconfigured to expect an ASGI application, it may invoke the ASGI handler incorrectly, leading to the missing
      `send` argument.
    - **Likely Cause**: The application is being run with an ASGI configuration (e.g., via `project.asgi:application`)
      instead of WSGI, or there’s a mix-up in the entry point.

2. **Incorrect ASGI Server Configuration**:
    - If you’re using an ASGI server (e.g., Uvicorn, Daphne) instead of Gunicorn, the server might not be passing the
      `send` argument correctly due to:
        - Incorrect ASGI application import (e.g., importing `project.wsgi` instead of `project.asgi`).
        - A misconfigured ASGI server command that doesn’t align with Django’s ASGI expectations.

3. **Code or Configuration Error**:
    - The `project/asgi.py` file might have been modified to incorrectly instantiate or call the ASGI handler.
    - The `docker-compose.yml` command might be running an ASGI server (e.g., `uvicorn project.asgi:application`)
      instead of Gunicorn with WSGI.
    - A dependency or middleware might be attempting to use ASGI features in a WSGI context.

4. **Docker or Environment Issue**:
    - The Docker container might be running a different command than intended (e.g., overriding `CMD` with an ASGI
      command).
    - A cached Docker image or volume might contain an outdated configuration.

Given your setup:

- You’re using **Gunicorn** (WSGI) in `docker-compose.yml`:
  ```yaml
  command: >
    sh -c "python manage.py migrate &&
           python manage.py collectstatic --noinput &&
           gunicorn --bind 0.0.0.0:8000 project.wsgi:application"
  ```
- The `project/asgi.py` is included but not referenced in the command, so it shouldn’t be causing issues unless
  explicitly invoked.
- The error suggests that something is attempting to treat the application as ASGI.

---

### Potential Causes in Your Project

Based on the project structure and files provided (April 28, 2025), here are the most likely causes:

1. **Incorrect Command in `docker-compose.yml`**:
    - If the `command` in `docker-compose.yml` was accidentally changed to use `project.asgi:application` (e.g.,
      `gunicorn --bind 0.0.0.0:8000 project.asgi:application` or `uvicorn project.asgi:application`), Gunicorn would try
      to run an ASGI application, which it can’t handle, leading to the error.
    - **Check**: Ensure `docker-compose.yml` uses `project.wsgi:application`.

2. **Manual Run Outside Docker**:
    - If you ran the application manually (e.g., `python manage.py runserver` or `uvicorn project.asgi:application`)
      instead of using `docker-compose up`, you might have used an ASGI command incorrectly.
    - **Check**: Confirm you’re running via `docker-compose up --build`.

3. **Modified `project/asgi.py`**:
    - The provided `project/asgi.py` is standard:
      ```python
      import os
      from django.core.asgi import get_asgi_application
 
      os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
      application = get_asgi_application()
      ```
    - If this file was altered (e.g., custom ASGI middleware or incorrect `application` definition), it could cause the
      handler to be called without `send`.
    - **Check**: Verify `project/asgi.py` matches the artifact.

4. **Gunicorn ASGI Attempt**:
    - Gunicorn supports ASGI with specific workers (e.g., `uvicorn.workers.UvicornWorker`), but your `requirements.txt`
      doesn’t include `uvicorn`:
      ```text
      django==4.2.11
      djangorestframework==3.15.1
      gunicorn==22.0.0
      ```
    - If Gunicorn is configured to use an ASGI worker (e.g., via `--worker-class uvicorn.workers.UvicornWorker`), it
      might misinvoke the ASGI handler.
    - **Check**: Ensure Gunicorn uses WSGI (default worker).

5. **Docker Cache or Volume Issue**:
    - A cached Docker image or volume might contain an outdated `project/asgi.py` or configuration that references ASGI.
    - **Check**: Rebuild the image and clear volumes.

---

### Steps to Fix the Error

Let’s resolve the issue systematically, ensuring compatibility with your SQLite-based Django project.

#### 1. Verify `docker-compose.yml`

Ensure the `command` uses `project.wsgi:application`, not `project.asgi:application`.

**Check**:

```yaml
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
      - ./annotations:/app/annotations
      - ./project:/app/project
      - ./annotations.db:/app/annotations.db
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --bind 0.0.0.0:8000 project.wsgi:application"
    ports:
      - "8000:8000"
```

**Action**:

- If `project.asgi:application` appears, change it to `project.wsgi:application`.
- If `uvicorn` or another ASGI server is referenced, replace with Gunicorn as above.
- Save and rebuild:
  ```bash
  docker-compose down
  docker-compose up --build
  ```

#### 2. Check `project/asgi.py`

Ensure `project/asgi.py` is correct and hasn’t been modified.

**Expected Content**:

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_asgi_application()
```

**Action**:

- Compare with the artifact (ID: `3152bb5e-b698-4d23-91f6-ae78bbbd8078`).
- If modified, revert to the above.
- If you don’t need ASGI (e.g., no WebSockets), you can safely ignore this file since Gunicorn uses
  `project.wsgi:application`.

#### 3. Verify `project/wsgi.py`

Ensure `project/wsgi.py` is correct, as this is the entry point for Gunicorn.

**Expected Content**:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_wsgi_application()
```

**Action**:

- Confirm it matches the artifact (ID: `b4c0ae3a-a360-46e0-a4b0-ef41e8288ec1`).
- If modified, revert to the above.

#### 4. Rebuild Docker Image

Clear cached images and volumes to ensure no outdated configurations.

**Action**:

```bash
docker-compose down -v  # Remove containers and volumes
docker system prune -f  # Remove unused images
docker-compose up --build
```

#### 5. Check Running Command

If you’re not using Docker Compose, you might have run an incorrect command.

**Incorrect Examples**:

```bash
gunicorn --bind 0.0.0.0:8000 project.asgi:application  # Wrong: ASGI with Gunicorn
uvicorn project.asgi:application  # ASGI server without proper setup
```

**Correct Command** (via Docker Compose):

- Use `docker-compose.yml` as provided.
- If running manually:
  ```bash
  python manage.py migrate
  python manage.py collectstatic --noinput
  gunicorn --bind 0.0.0.0:8000 project.wsgi:application
  ```

**Action**:

- Always use `docker-compose up --build` to ensure consistency.
- If testing locally, install dependencies:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```
- Run the correct Gunicorn command above.

#### 6. Check Dependencies

Ensure no ASGI-related dependencies (e.g., `uvicorn`, `daphne`) were accidentally added.

**Expected `requirements.txt`**:

```text
django==4.2.11
djangorestframework==3.15.1
gunicorn==22.0.0
```

**Action**:

- Verify `requirements.txt` matches the artifact (ID: `e8a19ad9-61ba-4c11-8377-5db1beeb11a7`).
- If `uvicorn` or `daphne` is present, remove them:
  ```bash
  nano requirements.txt  # Remove ASGI packages
  docker-compose up --build
  ```

#### 7. Test with Django Development Server

To isolate the issue, run the Django development server (WSGI-based) locally.

**Action**:

```bash
cd project
python manage.py migrate
python manage.py runserver 8000
```

- Access `http://localhost:8000`.
- If it works, the issue is specific to Gunicorn or Docker configuration.
- If the error persists, check `settings.py` for misconfigurations.

#### 8. Inspect Docker Logs

Get detailed error information.

**Action**:

```bash
docker ps  # Find container name
docker logs <app-container>
```

- Look for:
    - References to `project.asgi:application`.
    - Gunicorn worker errors.
    - Import errors or middleware issues.

#### 9. Update Gunicorn Configuration (If Needed)

If Gunicorn is attempting to use an ASGI worker, explicitly set the WSGI worker.

**Modify `docker-compose.yml`**:
Add `--worker-class sync` to ensure WSGI:

```yaml
command: >
  sh -c "python manage.py migrate &&
         python manage.py collectstatic --noinput &&
         gunicorn --worker-class sync --bind 0.0.0.0:8000 project.wsgi:application"
```

**Action**:

- Update and rebuild:
  ```bash
  docker-compose down
  docker-compose up --build
  ```

---

### If You Need ASGI (Unlikely)

If you intentionally want to use ASGI (e.g., for WebSockets or async features), you’ll need to:

1. Install an ASGI server:
   ```text
   # Add to requirements.txt
   uvicorn==0.30.6
   ```
2. Update `docker-compose.yml`:
   ```yaml
   command: >
     sh -c "python manage.py migrate &&
            python manage.py collectstatic --noinput &&
            uvicorn --host 0.0.0.0 --port 8000 project.asgi:application"
   ```
3. Rebuild:
   ```bash
   docker-compose up --build
   ```

However, your project (annotations with SQLite, REST APIs) doesn’t require ASGI, as it uses synchronous Django REST
Framework APIs. Stick with Gunicorn and WSGI unless you plan to add async features.

---

### Debugging Checklist

1. **Confirm Command**:
    - Check `docker-compose.yml` for `gunicorn ... project.wsgi:application`.
2. **Inspect Files**:
    - Verify `project/asgi.py` and `project/wsgi.py` are unchanged.
3. **Check Logs**:
    - Run `docker logs <app-container>` for clues.
4. **Rebuild**:
    - Clear cache: `docker-compose down -v && docker system prune -f`.
    - Rebuild: `docker-compose up --build`.
5. **Test Locally**:
    - Run `python manage.py runserver 8000` to bypass Docker.
6. **Dependencies**:
    - Ensure `requirements.txt` has no ASGI packages.

---

### Example: Expected Output

After fixing, running `docker-compose up --build` should show:

```
app_1  | [2025-04-28 12:00:00 +0000] [1] [INFO] Starting gunicorn 22.0.0
app_1  | [2025-04-28 12:00:00 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
app_1  | [2025-04-28 12:00:00 +0000] [1] [INFO] Using worker: sync
```

Access `http://localhost:8000` to see the annotation interface (`index.html`).

---

### If the Issue Persists

If the error remains after trying the above:

1. **Share Logs**:
    - Run `docker logs <app-container>` and share the full output.
2. **Share `docker-compose.yml`**:
    - Confirm the exact `command` being used.
3. **Check Running Processes**:
    - Inside the container:
      ```bash
      docker exec -it <app-container> ps aux
      ```
    - Look for `gunicorn` vs. `uvicorn` or other processes.
4. **Test Minimal Setup**:
    - Create a new `docker-compose.yml` with only:
      ```yaml
      version: '3.8'
      services:
        app:
          build: .
          command: gunicorn --bind 0.0.0.0:8000 project.wsgi:application
          ports:
            - "8000:8000"
      ```
    - Run `docker-compose up --build`.

---

### Updated Artifacts (If Needed)

The provided `docker-compose.yml`, `project/asgi.py`, and `project/wsgi.py` should be correct, but here’s a quick check:

- **docker-compose.yml** (ensure WSGI):
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

- **project/wsgi.py** (confirm standard):
  ```python
  import os
  from django.core.wsgi import get_wsgi_application

  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
  application = get_wsgi_application()
  ```

- **project/asgi.py** (optional, revert if modified):
  ```python
  import os
  from django.core.asgi import get_asgi_application

  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
  application = get_asgi_application()
  ```

---

### Summary

The `ASGIHandler.__call__() missing 1 required positional argument: 'send'` error is likely caused by:

- Running `project.asgi:application` with Gunicorn or an incorrect server.
- A misconfigured `docker-compose.yml` or manual command.
- An altered `project/asgi.py` or cached Docker image.

**Fix**:

- Ensure `docker-compose.yml` uses `gunicorn ... project.wsgi:application`.
- Rebuild Docker image: `docker-compose down -v && docker-compose up --build`.
- Verify `project/asgi.py` and `project/wsgi.py`.
- Avoid ASGI unless needed (no `uvicorn` or ASGI workers).

**Next Steps**:

- Apply the fixes above.
- Share `docker logs <app-container>` if the error persists.
- Confirm if you’re using Docker Compose or a manual command.
- Test `http://localhost:8000` to verify the annotation system works.

Let me know the results or any additional details!