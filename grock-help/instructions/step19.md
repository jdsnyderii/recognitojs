Thank you for the clarifications! I understand you’d like to switch from Flask to **Django** for the backend due to its
simplicity and performance, revert to **PostgreSQL** for annotation storage (as in our April 20, 2025, discussions), and
incorporate **canonicalized URLs** for the permalink to ensure consistency across pages. You also want to defer adding *
*Okta SAML** authentication for `currentUser` until later, relying on the `#user-input` field for now. These changes
build on our previous work (artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb` for `index.html`), replacing the S3/Flask
approach with a Django backend while meeting your requirements for annotation structure (user, timestamp, permalink in
JSONB) and multi-editor, multi-page support.

Below, I’ll outline the approach, incorporating:

- **Django backend** with PostgreSQL for annotation storage.
- **Canonicalized URLs** for permalinks (e.g., normalized `window.location.href`).
- **Annotation structure**: Unique identifier with user, timestamp (`version` in JSONB), and permalink.
- **Preserve features**: Sidebar toggle, highlight toggling, multi-user filter, instructions overlay, “Clear
  Annotations,” export/import.
- **Concurrency**: Optimistic locking using `version` for 2–5 editors.
- **Multi-page support**: Annotations bundled by permalink for pages across sites.
- **Docker deployment**: Based on our April 20, 2025, Django setup.

I’ll provide updated artifacts for `index.html` (same `artifact_id`), Django files (`settings.py`, `urls.py`,
`views.py`, models), Docker Compose, and PostgreSQL schema. Since you’re deferring Okta, I’ll use `#user-input` for
`currentUser`.

---

### Clarification and Assumptions

Based on your request and prior context, here’s the refined scope:

1. **Django Backend**:
    - Replace Flask with Django for simplicity and performance (e.g., built-in ORM, admin interface).
    - Use Django REST Framework (DRF) for REST APIs to handle PostgreSQL queries.
    - Host static `index.html` via Django’s static files or Nginx (as in April 20, 2025).

2. **PostgreSQL with JSONB**:
    - Store annotations in a table (`annotations`) with a **JSONB** column for flexible updates.
    - Columns:
        - `id`: Primary key (auto-incremented).
        - `user`: String (from `#user-input`).
        - `permalink`: String (canonicalized URL, e.g., `https://example.com/index.html`).
        - `annotation`: JSONB (RecogitoJS format with `id`, `body`, `target`, `creator`, `version`).
        - `timestamp`: Timestamp for creation/update.
    - Unique constraint: `(user, permalink, annotation__id)` (using JSONB path).
    - Index on `permalink` for fast filtering.

3. **Annotation Structure**:
    - **Unique Identifier**: Combine `user`, `permalink`, and `annotation.id` (in JSONB) to ensure uniqueness per user
      per page.
    - **Timestamp**: Store in `timestamp` column and `version` field (ISO 8601) in JSONB for concurrency.
    - **Permalink**: Canonicalized URL (e.g., remove query params, normalize protocol/host).
    - Example JSONB:
      ```json
      {
        "id": "anno-1",
        "body": [{ "value": "Great point!", "purpose": "commenting" }],
        "target": { "selector": [{ "type": "TextQuoteSelector", "exact": "sample paragraph" }] },
        "creator": { "type": "Person", "name": "Alice" },
        "version": "2025-04-26T18:37:00Z"
      }
      ```

4. **Canonicalized URLs**:
    - Normalize `window.location.href` to a consistent format:
        - Use `https` (or `http` for localhost).
        - Remove query params and fragments (e.g., `?id=123`, `#section`).
        - Standardize host/path (e.g., `example.com/index.html`).
    - Example: `http://localhost:8000/index.html?test=1` → `http://localhost:8000/index.html`.

5. **Multi-Editor and Multi-Page**:
    - Support 2–5 editors with optimistic locking (check `version` before saving).
    - Bundle annotations by `permalink` to support multiple pages (e.g., `index.html`, `about.html`) across sites (e.g.,
      `example.com`, `localhost`).
    - “Refresh Annotations” button to sync changes from other editors.

6. **Preserve Features**:
    - Sidebar toggle, highlight toggling (one annotation when sidebar open), multi-user filter, instructions overlay,
      “Clear Annotations,” export/import.
    - Update “Clear Annotations” to delete all annotations for the current `permalink` in PostgreSQL.

7. **Concurrency**:
    - Use `version` in JSONB for optimistic locking; alert user to refresh if a newer version exists.
    - PostgreSQL transactions ensure atomic updates.

8. **No Okta**:
    - Use `#user-input` for `currentUser` (stored in `localStorage` for persistence).
    - Defer Okta SAML integration.

9. **Docker Deployment**:
    - Use Docker Compose with Django, PostgreSQL, and Nginx (based on April 20, 2025).
    - Serve static `index.html` via Nginx, proxy API requests to Django.

**Assumptions**:

- **Django Version**: 4.2 (stable, aligns with April 20, 2025).
- **Canonicalization**: Remove query params/fragments, use `window.location.origin + pathname`.
- **Permalink**: Stored as `http://localhost:8000/index.html` locally, or `https://<domain>/index.html` in production.
- **Concurrency**: Optimistic locking for 2–5 editors; no need for strict transaction isolation.
- **JSONB Updates**: Allow updating `body` and `version`; full annotation updates for simplicity.
- **Clear Annotations**: Deletes all annotations for the `permalink`.
- **Deployment**: Local Docker Compose; production-ready with Nginx.

**Questions** (answered based on your input):

- **Backend**: Django, not Flask.
- **Authentication**: No Okta; use `#user-input`.
- **Permalink**: Canonicalized URLs.
- **Concurrency**: Optimistic locking sufficient.
- **Multi-Site**: Pages on different domains (e.g., `localhost`, `example.com`).

If any assumptions need tweaking (e.g., specific canonicalization rules, JSONB update fields), please clarify.

---

### Challenges and Considerations

1. **Django vs. Flask**:
    - Django’s ORM and DRF simplify database interactions and serialization.
    - More setup (e.g., `settings.py`, `urls.py`) but aligns with our April 20, 2025, work.
    - Performance is comparable for low concurrency; Django’s admin is a bonus.

2. **Canonicalized URLs**:
    - Normalize URLs client-side to avoid inconsistencies (e.g., `http` vs. `https`).
    - Handle localhost vs. production (e.g., `http://localhost:8000` vs. `https://example.com`).

3. **PostgreSQL with JSONB**:
    - JSONB allows flexible updates (e.g., `annotation->'body'`).
    - Unique constraint on JSONB path (`annotation->>'id'`) requires PostgreSQL 15+ or custom indexing.

4. **Concurrency**:
    - Optimistic locking checks `version`; sufficient for 2–5 editors.
    - Transactions prevent race conditions during updates.

5. **Static Site with Backend**:
    - `index.html` uses `fetch` for Django APIs.
    - Nginx serves static files, proxies `/api/` to Django.

6. **Multi-Page Support**:
    - `permalink` column ensures annotations are grouped correctly.
    - Canonicalization prevents duplicate permalinks.

---

### Proposed Approach

1. **PostgreSQL Schema**:
    - Table: `annotations`.
    - Columns: `id` (serial), `user` (varchar), `permalink` (varchar), `annotation` (JSONB), `timestamp` (timestamptz).
    - Unique constraint: `(user, permalink, annotation__id)`.
    - Index: `permalink`.

2. **Django Backend**:
    - App: `annotations`.
    - Model: `Annotation` with JSONB field.
    - DRF APIs:
        - `GET /api/annotations/`: Filter by `permalink`.
        - `POST /api/annotations/`: Create/update with optimistic locking.
        - `DELETE /api/annotations/<id>/`: Delete by `user`, `permalink`, `id`.
        - `DELETE /api/annotations/`: Clear by `permalink`.
    - Settings: Configure PostgreSQL, DRF, CORS.

3. **Canonicalized URLs**:
    - Client-side: `window.location.origin + window.location.pathname`.
    - Example: `http://localhost:8000/index.html?test=1` → `http://localhost:8000/index.html`.

4. **Frontend (`index.html`)**:
    - Replace S3/`localStorage` with `fetch` to Django APIs.
    - Use canonicalized `permalink`.
    - Add `version` to annotations.
    - Include “Refresh Annotations” button.
    - Preserve all features.

5. **Concurrency**:
    - Check `version` before saving; alert if conflict.
    - Use Django’s ORM for transactional updates.

6. **Docker Deployment**:
    - Django, PostgreSQL, Nginx.
    - Static files in `static/`; `index.html` served by Nginx.

---

### Updated Artifacts

I’ll provide:

- **Updated `index.html`**: Same `artifact_id` (`96200c6f-b303-426e-9559-95ac0eebd8bb`).
- **Django files**: `settings.py`, `urls.py`, `models.py`, `views.py`, `serializers.py`.
- **Docker Compose**: `docker-compose.yml`, `Dockerfile`, `nginx.conf`.
- **PostgreSQL Schema**: `schema.sql`.

#### 1. Updated `index.html`

- Uses `fetch` for Django APIs.
- Canonicalizes `permalink`.
- Adds `version` and “Refresh Annotations”.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecogitoJS Annotations with PostgreSQL</title>
    <link href="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.js"></script>
    <style>
        body {
            display: flex;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        #content {
            flex: 1;
            max-width: 70%;
            padding: 20px;
            background: #f9f9f9;
            border: 1px solid #ddd;
            position: relative;
            z-index: 1;
        }
        #content.no-highlights .r6o-annotation {
            background: none !important;
            border: none !important;
            box-shadow: none !important;
        }
        #content.no-highlights .r6o-annotation.active-highlight {
            background: rgba(255, 255, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 0, 0.5) !important;
        }
        #sidebar {
            width: 25%;
            min-width: 200px;
            padding: 20px;
            background: #fff;
            border-left: 1px solid #ddd;
            position: fixed;
            right: 0;
            top: 20px;
            bottom: 20px;
            overflow-y: auto;
            transition: transform 0.3s ease;
            z-index: 2;
        }
        #sidebar.hidden {
            transform: translateX(100%);
        }
        #sidebar-toggle-container {
            position: fixed;
            right: 0;
            top: 20px;
            z-index: 3;
        }
        #sidebar-toggle {
            padding: 8px 12px;
            background: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px 0 0 4px;
            cursor: pointer;
            font-size: 0.9em;
        }
        .annotation-comment {
            margin-bottom: 15px;
            padding: 10px;
            background: #e6f3ff;
            border-radius: 4px;
            position: relative;
            cursor: pointer;
        }
        .annotation-comment:hover {
            background: #d1e7ff;
        }
        .annotation-comment .quote {
            font-style: italic;
            color: #555;
            margin-bottom: 5px;
        }
        .annotation-comment .comment {
            font-weight: bold;
        }
        .annotation-comment .creator {
            font-size: 0.9em;
            color: #777;
            margin-top: 5px;
        }
        #controls {
            margin-bottom: 20px;
        }
        #controls button, #controls input, #controls select {
            margin-right: 10px;
            margin-bottom: 10px;
            padding: 8px 12px;
            cursor: pointer;
        }
        #user-input {
            padding: 8px;
            width: 150px;
        }
        #user-filter {
            width: 200px;
            height: 80px;
        }
        #instructions-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 4;
        }
        #instructions-overlay.hidden {
            display: none;
        }
        #instructions-content {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        #instructions-content h2 {
            margin-top: 0;
            font-size: 1.5em;
        }
        #instructions-content p {
            margin: 10px 0;
            line-height: 1.5;
        }
        #instructions-content button {
            background: #007bff;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
        }
        #instructions-content button:hover {
            background: #0056b3;
        }
        @media (max-width: 768px) {
            body {
                flex-direction: column;
            }
            #content {
                max-width: 100%;
            }
            #sidebar {
                position: static;
                width: 100%;
                margin-top: 20px;
                transform: none;
            }
            #sidebar.hidden {
                display: none;
            }
            #sidebar-toggle-container {
                position: static;
                margin-bottom: 10px;
            }
            #sidebar-toggle {
                width: 100%;
                border-radius: 4px;
            }
            #instructions-content {
                width: 95%;
                padding: 15px;
            }
        }
    </style>
</head>
<body>
<div id="content">
    <p>Text to annotate. This is a sample paragraph with some content that you can highlight and comment on. Try
        selecting different parts of this text to add annotations.</p>
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
        <button id="instructions-button">Show Instructions</button>
    </div>
    <div id="annotation-list"></div>
</div>
<div id="instructions-overlay" class="hidden">
    <div id="instructions-content">
        <h2>Annotation Instructions</h2>
        <p><strong>Create Annotations:</strong> Select text in the main content, type a comment, and enter your name in
            the user input field to save it.</p>
        <p><strong>Highlighting:</strong> When the sidebar is closed, all annotations are highlighted in yellow. When
            open, no highlights show unless you toggle one.</p>
        <p><strong>Toggling Highlights:</strong> Click an annotation in the sidebar to show its highlight in the text.
            Click again to hide it. Only one annotation can be highlighted at a time.</p>
        <p><strong>Other Features:</strong> Use the user filter to view specific users' annotations, refresh to sync
            changes, clear all annotations, or export/import them as JSON.</p>
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
    userInput.value = currentUser;
    updateSidebarVisibility();

    // Canonicalize URL
    function getCanonicalPermalink() {
        return window.location.origin + window.location.pathname;
    }

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
            toggleButton.textContent = 'Show';
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

    // Load annotations
    async function loadAnnotations() {
        try {
            const permalink = getCanonicalPermalink();
            const response = await fetch(`/api/annotations/?permalink=${encodeURIComponent(permalink)}`);
            if (!response.ok) throw new Error('Failed to load annotations');
            const annotations = await response.json();
            r.setAnnotations(annotations);
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Loaded annotations:', annotations);
        } catch (error) {
            console.error('Error loading annotations:', error);
            alert('Failed to load annotations from server.');
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
            const response = await fetch('/api/annotations/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: currentUser, permalink, annotation: updatedAnnotation })
            });
            if (!response.ok) {
                const error = await response.json();
                if (error.detail.includes('conflict')) {
                    alert('Annotation was updated by another user. Please refresh.');
                    return;
                }
                throw new Error('Failed to save annotation');
            }
            const annotations = await fetchAnnotations();
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Annotation saved:', updatedAnnotation);
        } catch (error) {
            console.error('Error saving annotation:', error);
            alert('Failed to save annotation to server.');
        }
    }

    // Fetch annotations
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
            if (!response.ok) throw new Error('Failed to clear annotations');
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
            updateSidebar([]);
            updateUserFilter([]);
            console.log('Annotations cleared');
        } catch (error) {
            console.error('Error clearing annotations:', error);
            alert('Failed to clear annotations from server.');
        }
    }

    // Refresh annotations
    async function refreshAnnotations() {
        await loadAnnotations();
        console.log('Annotations refreshed');
    }

    // Export annotations
    async function exportAnnotations() {
        try {
            const annotations = await fetchAnnotations();
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
                    for (const annotation of annotations) {
                        const version = new Date().toISOString();
                        const updatedAnnotation = { ...annotation, version };
                        await fetch('/api/annotations/', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ user: currentUser, permalink, annotation: updatedAnnotation })
                        });
                    }
                    r.setAnnotations(annotations);
                    selectedAnnotationId = null;
                    updateSidebar(annotations);
                    updateUserFilter(annotations);
                    console.log('Imported annotations:', annotations);
                } catch (error) {
                    console.error('Error importing annotations:', error);
                    alert('Failed to import annotations to server.');
                }
            };
            reader.readAsText(file);
        }
    });

    // Handle filter changes
    document.getElementById('user-filter').addEventListener('change', async () => {
        const annotations = await fetchAnnotations();
        updateSidebar(annotations);
    });

    // Handle annotation events
    r.on('createAnnotation', saveAnnotation);
    r.on('updateAnnotation', saveAnnotation);
    r.on('deleteAnnotation', async (annotation) => {
        try {
            const response = await fetch(`/api/annotations/${annotation.id}/`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: currentUser, permalink: getCanonicalPermalink() })
            });
            if (!response.ok) throw new Error('Failed to delete annotation');
            const annotations = await fetchAnnotations();
            updateSidebar(annotations);
            updateUserFilter(annotations);
            if (selectedAnnotationId === annotation.id) {
                selectedAnnotationId = null;
            }
            console.log('Annotation deleted:', annotation);
        } catch (error) {
            console.error('Error deleting annotation:', error);
            alert('Failed to delete annotation from server.');
        }
    });

    // Initialize
    loadAnnotations();
</script>
</body>
</html>
```

#### 2. Django Project Structure

Directory:

```
project/
├── annotations/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   └── index.html
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
└── requirements.txt
```

#### 3. Django Settings (`settings.py`)

- Configures PostgreSQL, DRF, CORS.

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'annotations',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True  # Adjust for production

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
        'NAME': os.getenv('POSTGRES_DB', 'annotations'),
        'USER': os.getenv('POSTGRES_USER', 'user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'password'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

#### 4. Django Project URLs (`urls.py`)

- Routes API and static files.

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

#### 5. Django App Models (`models.py`)

- Defines `Annotation` model with JSONB.

```python
from django.db import models
from django.contrib.postgres.fields import JSONBField


class Annotation(models.Model):
    user = models.CharField(max_length=255)
    permalink = models.CharField(max_length=2048)
    annotation = JSONBField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'permalink'],
                name='unique_annotation',
                condition=models.Q(annotation__id__isnull=False),
                include=['annotation__id']
            )
        ]
        indexes = [
            models.Index(fields=['permalink'])
        ]

    def __str__(self):
        return f"{self.user} - {self.annotation.get('id', 'No ID')}"
```

#### 6. Django App Serializers (`serializers.py`)

- Serializes `Annotation` model.

```python
from rest_framework import serializers
from .models import Annotation


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['user', 'permalink', 'annotation', 'timestamp']
```

#### 7. Django App Views (`views.py`)

- API views for CRUD operations.

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Annotation
from .serializers import AnnotationSerializer
from django.db.models import Q
from django.db import transaction


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

    def get_queryset(self):
        permalink = self.request.query_params.get('permalink')
        if permalink:
            return self.queryset.filter(permalink=permalink)
        return self.queryset

    def create(self, request):
        user = request.data.get('user', 'Anonymous')
        permalink = request.data.get('permalink')
        annotation = request.data.get('annotation')
        if not (user and permalink and annotation):
            return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            existing = Annotation.objects.filter(
                user=user,
                permalink=permalink,
                annotation__id=annotation.get('id')
            ).first()
            if existing and existing.annotation.get('version') > annotation.get('version'):
                return Response({'detail': 'Version conflict'}, status=status.HTTP_409_CONFLICT)

            if existing:
                existing.annotation = annotation
                existing.save()
                serializer = self.get_serializer(existing)
                return Response(serializer.data)
            else:
                serializer = self.get_serializer(data={'user': user, 'permalink': permalink, 'annotation': annotation})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)

    def destroy(self, request, pk=None):
        user = request.data.get('user', 'Anonymous')
        permalink = request.data.get('permalink')
        if not (user and permalink):
            return Response({'detail': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        annotation = self.get_queryset().filter(
            user=user,
            permalink=permalink,
            annotation__id=pk
        ).first()
        if not annotation:
            return Response({'detail': 'Annotation not found'}, status=status.HTTP_404_NOT_FOUND)
        annotation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        permalink = request.query_params.get('permalink')
        if not permalink:
            return Response({'detail': 'Permalink required'}, status=status.HTTP_400_BAD_REQUEST)
        self.get_queryset().filter(permalink=permalink).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### 8. Django App URLs (`annotations/urls.py`)

- API routes.

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnotationViewSet

router = DefaultRouter()
router.register(r'annotations', AnnotationViewSet, basename='annotation')

urlpatterns = [
    path('', include(router.urls)),
]
```

#### 9. Django Migration (`migrations/0001_initial.py`)

- Creates `annotations` table.

```python
from django.db import migrations, models
import django.contrib.postgres.fields.jsonb


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=255)),
                ('permalink', models.CharField(max_length=2048)),
                ('annotation', django.contrib.postgres.fields.jsonb.JSONField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(
                        fields=['user', 'permalink'],
                        name='unique_annotation',
                        condition=models.Q(annotation__id__isnull=False),
                        include=['annotation__id']
                    )
                ],
            },
        ),
        migrations.AddIndex(
            model_name='Annotation',
            index=models.Index(fields=['permalink'], name='annotations_permalink_idx'),
        ),
    ]
```

#### 10. Docker Compose (`docker-compose.yml`)

- Django, PostgreSQL, Nginx.

```yaml
version: '3.8'
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:80"
    depends_on:
      - app
    volumes:
      - ./static:/usr/share/nginx/html
      - ./staticfiles:/staticfiles
  app:
    image: python:3.13-slim
    command: gunicorn --bind 0.0.0.0:8000 project.wsgi:application
    volumes:
      - .:/app
    working_dir: /app
    depends_on:
      - db
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_DB=annotations
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=annotations
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

#### 11. Dockerfile

- Builds Django and Nginx.

```dockerfile
FROM nginx:alpine
COPY static /usr/share/nginx/html
COPY staticfiles /staticfiles
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### 12. Nginx Configuration (`nginx.conf`)

- Proxies API, serves static files.

```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /static/ {
        alias /staticfiles/;
    }
}
```

#### 13. Requirements (`requirements.txt`)

- Django dependencies.

Django==4.2
djangorestframework==3.15
psycopg2-binary==2.9
django-cors-headers==4.3
gunicorn==22.0

#### 14. PostgreSQL Schema (`schema.sql`)

- For manual setup (migrations handle this).

```sql
CREATE TABLE IF NOT EXISTS annotations (
    id SERIAL PRIMARY KEY,
    user VARCHAR(255) NOT NULL,
    permalink VARCHAR(2048) NOT NULL,
    annotation JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_annotation UNIQUE (user, permalink, (annotation->>'id'))
);
CREATE INDEX IF NOT EXISTS annotations_permalink_idx ON annotations (permalink);
```

---

### Setup Instructions

1. **Directory Structure**:
   ```
   project/
   ├── annotations/
   │   ├── migrations/
   │   │   └── 0001_initial.py
   │   ├── __init__.py
   │   ├── admin.py
   │   ├── apps.py
   │   ├── models.py
   │   ├── serializers.py
   │   ├── urls.py
   │   └── views.py
   ├── project/
   │   ├── __init__.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── static/
   │   └── index.html
   ├── staticfiles/
   ├── docker-compose.yml
   ├── Dockerfile
   ├── nginx.conf
   ├── requirements.txt
   └── schema.sql
   ```

2. **Install Docker**:
    - Ensure Docker and Docker Compose are installed.

3. **Create Django App**:
    - Save all files as shown.
    - Create empty `annotations/admin.py` and `annotations/apps.py`:
      ```python
      # admin.py
      from django.contrib import admin
      from .models import Annotation
      admin.site.register(Annotation)
      ```
      ```python
      # apps.py
      from django.apps import AppConfig
      class AnnotationsConfig(AppConfig):
          default_auto_field = 'django.db.models.BigAutoField'
          name = 'annotations'
      ```

4. **Build and Run**:
    - Run:
      ```bash
      docker-compose up --build
      ```
    - Access: `http://localhost:8000`.

5. **Apply Migrations**:
    - Run:
      ```bash
      docker exec -it <app-container> python manage.py migrate
      ```
    - Or manually apply `schema.sql`:
      ```bash
      docker exec -it <db-container> psql -U user -d annotations -f /path/to/schema.sql
      ```

6. **Collect Static Files**:
    - Run:
      ```bash
      docker exec -it <app-container> python manage.py collectstatic --noinput
      ```

7. **Test**:
    - Open `http://localhost:8000`.
    - Enter user name (e.g., “Alice”).
    - Create annotation; check PostgreSQL:
      ```sql
      SELECT * FROM annotations;
      ```
    - Verify `user`, `permalink` (e.g., `http://localhost:8000/index.html`), `timestamp`, `annotation->>'version'`.
    - Test all features: highlights, filter, instructions, clear, refresh, export/import.
    - Test multi-page:
        - Copy `index.html` to `static/about.html`.
        - Access `http://localhost:8000/about.html`.
        - Verify separate `permalink` rows.

8. **Test Concurrency**:
    - Open two browsers (e.g., Chrome, Firefox).
    - Create annotations as “Alice” and “Bob”; verify unique rows.
    - Update same annotation; check conflict alert.
    - Click “Refresh Annotations” to sync.

---

### How It Works

- **Annotation Storage**:
    - Stored in `annotations` table.
    - Example:
      ```sql
      id: 1
      user: 'Alice'
      permalink: 'http://localhost:8000/index.html'
      annotation: { "id": "anno-1", "body": [...], "creator": {"name": "Alice"}, "version": "2025-04-26T18:37:00Z" }
      timestamp: '2025-04-26 18:37:00+00'
      ```
    - Unique constraint: `(user, permalink, annotation->>'id')`.

- **Frontend**:
    - `index.html` calls Django APIs (`/api/annotations/`).
    - `getCanonicalPermalink()` normalizes URLs.
    - `version` ensures concurrency.

- **Backend**:
    - Django ORM with DRF:
        - `GET /api/annotations/`: Filters by `permalink`.
        - `POST /api/annotations/`: Upserts with version check.
        - `DELETE /api/annotations/<id>/`: Deletes by `user`, `permalink`, `id`.
        - `DELETE /api/annotations/`: Clears by `permalink`.
    - Transactions ensure atomicity.

- **Canonicalization**:
    - `window.location.origin + pathname` removes query params/fragments.

- **Concurrency**:
    - Checks `version`; alerts on conflicts.
    - Transactions prevent race conditions.

- **Multi-Page**:
    - Annotations grouped by `permalink`.
    - Supports `index.html`, `about.html`, etc.

---

### Limitations and Notes

- **Backend**: Django requires more setup than Flask but offers ORM and admin.
- **Canonicalization**: Simple normalization; may need custom rules (e.g., force `https`).
- **Concurrency**: Optimistic locking for low concurrency; stricter isolation possible.
- **JSONB Updates**: Full annotation updates; partial updates (e.g., `body`) can be added.
- **Okta**: Deferred; `#user-input` used for now.

---

### Testing Instructions

1. **Deploy**:
    - Run `docker-compose up --build`.
    - Access `http://localhost:8000`.

2. **Test Annotations**:
    - Create as “Alice”; verify in PostgreSQL.
    - Update/delete; check `timestamp`, `version`.
    - Clear; confirm empty `permalink` rows.

3. **Test Concurrency**:
    - Create annotations in two browsers.
    - Update same annotation; verify conflict alert.
    - Refresh to sync.

4. **Test Multi-Page**:
    - Add `about.html`; create annotations.
    - Verify separate `permalink` rows.

5. **Test Features**:
    - Toggle sidebar/highlights, filter, instructions, export/import.
    - Ensure all work with Django.

6. **Test Canonicalization**:
    - Access `http://localhost:8000/index.html?test=1`.
    - Verify `permalink`: `http://localhost:8000/index.html`.

7. **Responsive Design**:
    - Test on mobile (<768px).

---

### Troubleshooting

- **API Errors**:
    - Check Django logs: `docker logs <app-container>`.
    - Verify `POSTGRES_*` env vars.
- **Annotations Not Saving**:
    - Inspect `fetch` responses in Console.
    - Check PostgreSQL: `docker logs <db-container>`.
- **Concurrency Conflicts**:
    - Log `version` in `saveAnnotation`.
- **Permalink Issues**:
    - Log `getCanonicalPermalink()` output.
- **Provide Details**:
    - Share errors, browser, logs, or table contents.

---

### Enhancements (Optional)

- **Okta SAML**:
    - Add later for `currentUser` (as in April 26, 2025, S3 session).
- **Auto-Refresh**:
    - `setInterval(refreshAnnotations, 30000);`
- **Partial JSONB Updates**:
    - Add `PATCH /api/annotations/<id>/` for `body`.
- **Custom Canonicalization**:
    - Force `https`, handle subdomains.
- **Django Admin**:
    - Use `admin/` to manage annotations.

---

### Final Notes

- **Django** replaces Flask for simplicity/performance.
- **PostgreSQL** with **JSONB** stores annotations with `user`, `timestamp`, `permalink`.
- **Canonicalized URLs** ensure consistent permalinks.
- **No Okta**; uses `#user-input`.
- All features preserved; Docker deployment aligns with April 20, 2025.
- Test and let me know if adjustments are needed (e.g., Okta, custom canonicalization, or JSONB updates). Ready for more
  ideas!