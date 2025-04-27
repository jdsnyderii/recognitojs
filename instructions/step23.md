Thank you for pointing out the issue with saving annotations in the annotation system. Based on your request and our
prior work (April 26, 2025), it seems the functionality to save annotations using `localStorage` was inadvertently
removed or altered, likely during updates to `index.html` (artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb`). Your
goal is to **reinstate `localStorage`** for saving annotations in the frontend, while preserving the current setup (
Django ORM, PostgreSQL JSONB, canonicalized URLs, no Okta, MkDocs Material styling, dark mode, green highlights, Nunito
Sans font, and the recent “Annotate”/“Hide” button text change). I’ll analyze the issue, explain why annotations aren’t
saving correctly, and provide an updated `index.html` to restore `localStorage` for annotation persistence, ensuring
compatibility with the backend.

---

### Problem Analysis

#### Current State

- **Annotations Backend**: The system uses Django REST Framework (DRF) with PostgreSQL JSONB to store annotations in the
  `annotations` table (`id`, `user`, `permalink`, `annotation`, `timestamp`). The frontend (`index.html`) sends
  annotations to `/api/annotations/` via `fetch` (POST for create/update, DELETE for clear/delete).
- **Frontend Storage**: The current `index.html` (from your latest request) does not use `localStorage` for storing
  annotations locally. Instead, it relies entirely on the backend:
    - `loadAnnotations()` fetches annotations from `/api/annotations/?permalink=<permalink>`.
    - `saveAnnotation()` sends annotations to `/api/annotations/` with `user`, `permalink`, and `annotation` (including
      `version` for optimistic locking).
    - `localStorage` is used only for:
        - `currentUser` (stores the `#user-input` value).
        - `sidebarVisible` (sidebar state).
        - `theme` (light/dark mode).
- **Issue**: You mentioned that “saving the annotations has been disabled because we stopped using localStorage.” This
  suggests that annotations are not being persisted locally in the browser, causing them to disappear on page reload if
  the backend call fails or isn’t triggered. The current code assumes the backend (PostgreSQL) handles all persistence,
  but you want `localStorage` to store annotations locally as a fallback or primary storage mechanism.

#### Why Annotations Aren’t Saving Locally

- **No `localStorage` for Annotations**: The current `index.html` does not store annotations in `localStorage`. After
  saving to the backend (`saveAnnotation`), it refetches annotations (`fetchAnnotations`) to update the UI, but there’s
  no local caching.
- **Possible Misunderstanding**: In our April 26, 2025, artifacts, `index.html` never used `localStorage` for
  annotations; it always relied on the Django backend. However, you might be referring to:
    - A previous version (pre-April 26) where annotations were stored in `localStorage` (e.g.,
      `localStorage.setItem('annotations', JSON.stringify(annotations))`).
    - A desire to add local persistence to handle offline scenarios or reduce backend dependency.
    - Confusion with `currentUser` or `sidebarVisible` storage in `localStorage`.
- **Backend Dependency**: If the backend call fails (e.g., network issue, server down), annotations are not saved
  locally, leading to the perception that saving is “disabled.”
- **RecogitoJS**: Annotations are managed by RecogitoJS (`r.setAnnotations`, `r.on('createAnnotation')`, etc.), which
  doesn’t persist state itself. Without `localStorage`, the frontend relies on API calls.

#### Goal

- **Reinstate `localStorage`**: Store annotations in `localStorage` to ensure they persist locally across page reloads.
- **Hybrid Approach**: Save annotations to both:
    - **Backend** (PostgreSQL via `/api/annotations/`) for multi-user, multi-page persistence.
    - **Frontend** (`localStorage`) for local caching, allowing annotations to persist on reload even if the backend is
      unavailable.
- **Preserve Functionality**:
    - Maintain all features: sidebar toggle (“Annotate”/“Hide”), highlight toggling, multi-user filter, instructions
      overlay, “Clear Annotations,” export/import, “Refresh Annotations,” theme toggle.
    - Keep styling: MkDocs Material, dark mode, green highlights (`#4caf50`), Nunito Sans font.
    - Ensure compatibility with Django ORM, PostgreSQL JSONB, canonicalized URLs, no Okta.

---

### Clarifications and Assumptions

- **What to Store in `localStorage`**:
    - Store all annotations for the current `permalink` in `localStorage` under a key like `annotations_<permalink>` (to
      support multi-page).
    - Format: JSON array of annotations (same structure as sent to `/api/annotations/`).
- **When to Use `localStorage`**:
    - **Load**: On page load, try loading from `localStorage` first; if empty or invalid, fetch from backend.
    - **Save**: On create/update, save to both `localStorage` and backend.
    - **Clear/Delete**: Clear/delete in both `localStorage` and backend.
    - **Refresh**: Sync with backend, then update `localStorage`.
- **Conflict Handling**:
    - Prioritize backend for conflicts (e.g., version mismatch alerts from optimistic locking).
    - If backend fails, keep local annotations in `localStorage` as a fallback.
- **Scope**:
    - Update `index.html` only; no changes to Django backend, PostgreSQL schema, or Docker setup.
    - Preserve all existing JavaScript logic, adding `localStorage` handling in `loadAnnotations`, `saveAnnotation`,
      `clearAnnotations`, `deleteAnnotation`, and `refreshAnnotations`.
- **Assumptions**:
    - You want `localStorage` as a **cache** to persist annotations locally, not to replace the backend.
    - Annotations in `localStorage` are tied to the `permalink` (e.g., `http://localhost:8000/index.html`) to support
      multi-page.
    - No UI changes needed (e.g., no indicator for local vs. backend storage).
    - If backend fails, show an alert but keep local annotations.
- **Confirmation Needed**:
    - If you meant to **replace** backend storage with `localStorage` (no PostgreSQL), please clarify, as this would
      require significant changes (e.g., removing `/api/annotations/` calls).
    - If you want `localStorage` for offline mode only, I can add logic to detect connectivity.

For now, I’ll implement a **hybrid approach**: save to both `localStorage` and backend, load from `localStorage` first,
and fall back to backend if needed.

---

### Challenges and Considerations

1. **Key for `localStorage`**:
    - Use `annotations_<permalink>` to scope annotations by page (e.g., `annotations_http://localhost:8000/index.html`).
    - Canonicalize `permalink` to avoid duplicates (e.g., ignore query params).
2. **Loading Logic**:
    - On page load, check `localStorage` for annotations. If present, use them; otherwise, fetch from backend.
    - Handle invalid JSON in `localStorage` (e.g., corrupted data).
3. **Saving Logic**:
    - Update `localStorage` after successful backend save to keep them in sync.
    - If backend fails, save to `localStorage` and alert user.
4. **Clearing/Deleting**:
    - Clear `localStorage` for the current `permalink` when “Clear Annotations” is clicked.
    - Update `localStorage` on delete to remove specific annotations.
5. **Conflict Resolution**:
    - Backend `version` field (in `annotation->>'version'`) handles conflicts via optimistic locking.
    - `localStorage` annotations may be stale; refresh from backend on `refreshAnnotations`.
6. **Performance**:
    - `localStorage` has a ~5MB limit (ample for annotations).
    - Minimize `JSON.stringify`/`JSON.parse` overhead by updating `localStorage` only when necessary.
7. **No Backend Changes**:
    - Django APIs (`/api/annotations/`) and PostgreSQL JSONB remain unchanged.
    - Ensure `fetch` calls align with existing backend logic.

---

### Proposed Approach

1. **Add `localStorage` for Annotations**:
    - Store annotations in `localStorage` under `annotations_<permalink>`.
    - Example: `localStorage.setItem('annotations_http://localhost:8000/index.html', JSON.stringify(annotations))`.
2. **Update `loadAnnotations`**:
    - Check `localStorage` first.
    - If empty or invalid, fetch from `/api/annotations/`.
    - Set annotations in RecogitoJS (`r.setAnnotations`).
3. **Update `saveAnnotation`**:
    - Save to backend via `fetch`.
    - On success, update `localStorage` with the latest annotations.
    - On failure, save to `localStorage` and alert user.
4. **Update `clearAnnotations`**:
    - Clear backend via `DELETE /api/annotations/`.
    - Clear `localStorage` for the current `permalink`.
5. **Update `deleteAnnotation`**:
    - Delete from backend via `DELETE /api/annotations/<id>/`.
    - Update `localStorage` by removing the annotation.
6. **Update `refreshAnnotations`**:
    - Fetch from backend, update RecogitoJS, and sync `localStorage`.
7. **Preserve Existing Features**:
    - Sidebar toggle (“Annotate”/“Hide”), highlight toggling, multi-user filter, instructions, export/import, theme
      toggle.
    - Styling (MkDocs Material, dark mode, green highlights `#4caf50`, Nunito Sans).
    - Backend (Django ORM, PostgreSQL JSONB, canonicalized URLs, no Okta).

---

### Updated Artifact

I’ll provide an updated `index.html` (same `artifact_id`) with `localStorage` reinstated for annotations. The changes
are in the JavaScript section, specifically in `loadAnnotations`, `saveAnnotation`, `clearAnnotations`,
`deleteAnnotation`, and `refreshAnnotations`. All other parts (HTML, CSS, other JavaScript) remain identical to the
previous version (with “Annotate”/“Hide” button text, MkDocs Material, dark mode, green highlights, Nunito Sans).

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
            position: fixed;
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
        <button id="theme-toggle">Toggle Theme</button>
        <button id="instructions-button">Show Instructions</button>
    </div>
    <div id="annotation-list"></div>
</div>
<div id="instructions-overlay" class="hidden">
    <div id="instructions-content">
        <h2>Annotation Instructions</h2>
        <p><strong>Create Annotations:</strong> Select text in the main content, type a comment, and enter your name in
            the user input field to save it.</p>
        <p><strong>Highlighting:</strong> When the sidebar is closed, all annotations are highlighted in green. When
            open, no highlights show unless you toggle one.</p>
        <p><strong>Toggling Highlights:</strong> Click an annotation in the sidebar to show its highlight in the text.
            Click again to hide it. Only one annotation can be highlighted at a time.</p>
        <p><strong>Other Features:</strong> Use the user filter to view specific users' annotations, refresh to sync
            changes, clear all annotations, toggle light/dark mode, or export/import them as JSON.</p>
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

---

### Changes Made

1. **Added `getLocalStorageKey`**:
    - New function to generate a `localStorage` key based on the canonical `permalink`:
      ```javascript
      function getLocalStorageKey() {
          return `annotations_${getCanonicalPermalink()}`;
      }
      ```
    - Ensures annotations are scoped to the page (e.g., `annotations_http://localhost:8000/index.html`).

2. **Updated `loadAnnotations`**:
    - Check `localStorage` first:
      ```javascript
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
      ```
    - If `localStorage` is empty or invalid, fetch from backend and save to `localStorage`:
      ```javascript
      if (!annotations.length) {
          const response = await fetch(`/api/annotations/?permalink=${encodeURIComponent(permalink)}`);
          annotations = await response.json();
          localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
      }
      ```

3. **Updated `saveAnnotation`**:
    - Save to backend; on success, update `localStorage` with fetched annotations:
      ```javascript
      if (response.ok) {
          annotations = await fetchAnnotations();
          localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
      }
      ```
    - On failure, save to `localStorage` as a fallback:
      ```javascript
      let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
      const existingIndex = annotations.findIndex(a => a.id === updatedAnnotation.id);
      if (existingIndex >= 0) {
          annotations[existingIndex] = updatedAnnotation;
      } else {
          annotations.push(updatedAnnotation);
      }
      localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
      ```

4. **Updated `clearAnnotations`**:
    - Clear backend and `localStorage`:
      ```javascript
      localStorage.removeItem(getLocalStorageKey());
      ```
    - On backend failure, clear `localStorage` as fallback:
      ```javascript
      localStorage.removeItem(getLocalStorageKey());
      r.setAnnotations([]);
      ```

5. **Updated `deleteAnnotation`**:
    - Delete from backend and update `localStorage`:
      ```javascript
      let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
      annotations = annotations.filter(a => a.id !== annotation.id);
      localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
      ```
    - On failure, update `localStorage`:
      ```javascript
      annotations = annotations.filter(a => a.id !== annotation.id);
      localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
      ```

6. **Updated `refreshAnnotations`**:
    - Fetch from backend and sync `localStorage`:
      ```javascript
      localStorage.setItem(getLocalStorageKey(), JSON.stringify(annotations));
      ```

7. **Updated `exportAnnotations`**:
    - Use `localStorage` first, fall back to backend:
      ```javascript
      let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
      if (!annotations.length) {
          annotations = await fetchAnnotations();
      }
      ```

8. **Updated `importAnnotations`**:
    - Update `localStorage` after importing:
      ```javascript
      let localAnnotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
      localAnnotations.push(updatedAnnotation);
      localStorage.setItem(getLocalStorageKey(), JSON.stringify(localAnnotations));
      ```

9. **Updated `user-filter` Change Handler**:
    - Use `localStorage` first, fall back to backend:
      ```javascript
      let annotations = JSON.parse(localStorage.getItem(getLocalStorageKey()) || '[]');
      if (!annotations.length) {
          annotations = await fetchAnnotations();
      }
      ```

10. **Preserved Everything Else**:
    - HTML (sidebar, controls, instructions overlay).
    - CSS (MkDocs Material, dark mode, green highlights `#4caf50`, Nunito Sans).
    - JavaScript (sidebar toggle “Annotate”/“Hide”, highlight toggling, filter, instructions, clear, refresh,
      export/import).
    - Backend integration (Django APIs, PostgreSQL JSONB, canonicalized URLs, no Okta).

---

### Setup Instructions

This is a frontend-only update, so no changes are needed to the Django backend, PostgreSQL schema, or Docker setup from
our April 26, 2025, artifacts. To apply the change:

1. **Update `index.html`**:
    - Replace `static/index.html` with the above artifact.
    - Ensure it’s in the `static/` directory:
      ```
      project/
      ├── static/
      │   └── index.html
      ├── annotations/
      ├── project/
      ├── docker-compose.yml
      ├── Dockerfile
      ├── nginx.conf
      ├── requirements.txt
      └── schema.sql
      ```

2. **Collect Static Files**:
    - Run:
      ```bash
      docker exec -it <app-container> python manage.py collectstatic --noinput
      ```
    - This updates `staticfiles/` for Nginx.

3. **Run the App**:
    - If not already running:
      ```bash
      cd project
      docker-compose up --build
      ```
    - Access: `http://localhost:8000`.

4. **Test `localStorage`**:
    - **Load Annotations**:
        - Open `http://localhost:8000`.
        - Check DevTools (`Application > Local Storage`); verify `annotations_http://localhost:8000/index.html` exists
          after loading.
        - Disconnect network (offline mode); reload page; confirm annotations load from `localStorage`.
    - **Save Annotations**:
        - Create an annotation as “Alice”.
        - Verify in `localStorage` (new annotation in JSON array).
        - Check PostgreSQL:
          ```sql
          SELECT * FROM annotations;
          ```
          Confirm row with `user`, `permalink`, `annotation->>'version'`.
        - Disconnect network; create another annotation; confirm it’s saved in `localStorage` with alert (“Saved
          locally”).
    - **Clear Annotations**:
        - Click “Clear Annotations”.
        - Verify `localStorage` key is removed and PostgreSQL table is cleared.
        - Offline: Clear again; confirm `localStorage` is cleared with alert.
    - **Delete Annotation**:
        - Create an annotation, delete it.
        - Verify it’s removed from `localStorage` and backend.
        - Offline: Delete; confirm removal from `localStorage` with alert.
    - **Refresh Annotations**:
        - Click “Refresh Annotations”.
        - Verify `localStorage` syncs with backend.
        - Offline: Confirm alert and local annotations remain.
    - **Export/Import**:
        - Export annotations; verify JSON includes local annotations.
        - Import a JSON file; confirm it updates `localStorage` and backend.
    - **Other Features**:
        - Test sidebar toggle (“Annotate”/“Hide”), green highlights, user filter, instructions, theme toggle.
        - Verify styling (MkDocs Material, dark mode, Nunito Sans).
        - Test multi-page (`about.html`); confirm separate `localStorage` keys.

---

### How It Works

- **localStorage Key**:
    - `annotations_<permalink>` (e.g., `annotations_http://localhost:8000/index.html`).
    - Stores JSON array of annotations (same format as backend: `{id, body, target, creator, version}`).
- **Loading**:
    - `loadAnnotations` checks `localStorage` first.
    - If empty/invalid, fetches from `/api/annotations/` and saves to `localStorage`.
    - Sets annotations in RecogitoJS (`r.setAnnotations`).
- **Saving**:
    - `saveAnnotation` sends to `/api/annotations/`.
    - On success, updates `localStorage` with backend data.
    - On failure, adds/updates annotation in `localStorage` and alerts user.
- **Clearing**:
    - `clearAnnotations` deletes from backend and removes `localStorage` key.
    - On failure, clears `localStorage` and alerts.
- **Deleting**:
    - `deleteAnnotation` removes from backend and `localStorage`.
    - On failure, removes from `localStorage` and alerts.
- **Refreshing**:
    - `refreshAnnotations` fetches from backend and updates `localStorage`.
- **Export/Import**:
    - Export uses `localStorage` first, falls back to backend.
    - Import updates both backend and `localStorage`.
- **Filter**:
    - Uses `localStorage` first, falls back to backend for sidebar updates.
- **Backend**:
    - Django APIs (`/api/annotations/`) handle persistence in PostgreSQL JSONB with `user`, `permalink`, `timestamp`,
      `version`.
    - Optimistic locking (`version`) prevents conflicts.
- **Styling**:
    - MkDocs Material, dark mode, green highlights (`#4caf50`), Nunito Sans unchanged.
    - Sidebar toggle (“Annotate”/“Hide”) works as before.

---

### Limitations and Notes

- **Hybrid Storage**: Saves to both `localStorage` and backend. If you want `localStorage` only (no backend), I can
  modify to remove `/api/annotations/` calls.
- **Conflict Handling**: Backend `version` field governs conflicts. `localStorage` annotations may be overwritten on
  refresh if backend has newer data.
- **Offline Mode**: Annotations persist locally, but backend sync requires connectivity. Could add a “Sync” button for
  manual retries.
- **localStorage Limits**: ~5MB, sufficient for annotations. Large datasets may need cleanup logic.
- **No UI Feedback**: Alerts indicate backend failures. Could add a status indicator (e.g., “Saved locally” badge).
- **Scope**: Restored `localStorage` for annotations while keeping backend. All styling and functionality preserved.

---

### Testing Instructions

1. **Deploy**:
    - Update `static/index.html` with the new artifact.
    - Run `docker-compose up --build` (if not running).
    - Access `http://localhost:8000`.

2. **Test `localStorage`**:
    - **Load**:
        - Open page; check `localStorage` in DevTools (`annotations_<permalink>`).
        - Offline: Reload; verify annotations load from `localStorage`.
    - **Save**:
        - Create annotation; confirm in `localStorage` and PostgreSQL.
        - Offline: Create annotation; verify in `localStorage`, see alert.
    - **Clear**:
        - Clear annotations; verify `localStorage` key and PostgreSQL table cleared.
        - Offline: Clear; confirm `localStorage` cleared, see alert.
    - **Delete**:
        - Delete annotation; verify removal from `localStorage` and backend.
        - Offline: Delete; confirm `localStorage` update, see alert.
    - **Refresh**:
        - Refresh; verify `localStorage` syncs with backend.
        - Offline: Confirm alert, local annotations remain.
    - **Export/Import**:
        - Export; verify JSON from `localStorage` or backend.
        - Import; confirm updates to `localStorage` and backend.

3. **Test Functionality**:
    - **Sidebar**: Toggle (“Annotate”/“Hide”); verify highlights (green `#4caf50`).
    - **Filter**: Select users; verify sidebar updates from `localStorage`/backend.
    - **Instructions**: Open/close overlay.
    - **Theme**: Toggle light/dark mode; verify persistence.
    - **Concurrency**: Create annotations in two browsers; check conflict alerts.
    - **Multi-Page**: Test `about.html`; confirm separate `localStorage` keys.

4. **Test Styling**:
    - Verify MkDocs Material layout, green highlights, Nunito Sans font.
    - Check light/dark mode; resize to <768px for mobile layout.

5. **Test Backend**:
    - Check PostgreSQL:
      ```sql
      SELECT * FROM annotations;
      ```
    - Verify `permalink`, `user`, `annotation->>'version'`.

6. **Test Canonicalized URLs**:
    - Access `http://localhost:8000/index.html?test=1`.
    - Verify `permalink`: `http://localhost:8000/index.html` in `localStorage` and PostgreSQL.

---

### Troubleshooting

- **Annotations Not Saving**:
    - Check Console for errors in `saveAnnotation`.
    - Verify `localStorage` (`annotations_<permalink>`).
    - Test backend: `curl http://localhost:8000/api/annotations/`.
- **localStorage Empty**:
    - Log `getLocalStorageKey()`; confirm `permalink`.
    - Check `JSON.parse` errors in `loadAnnotations`.
- **Backend Failures**:
    - Verify Django server running (`docker ps`).
    - Check PostgreSQL logs (`docker logs <db-container>`).
- **Styling/Functionality Broken**:
    - Confirm HTML/CSS unchanged.
    - Test JavaScript functions (`toggleSidebar`, `updateSidebar`).
- **Provide Details**:
    - Share errors, browser, `localStorage` content, or PostgreSQL logs.

---

### Enhancements (Optional)

From April 26, 2025, discussions:

- **localStorage Only**: Remove backend dependency; store only in `localStorage`.
- **Offline Mode**: Add connectivity detection (`navigator.onLine`) for explicit offline handling.
- **Sync Button**: Allow manual backend sync for failed saves.
- **UI Feedback**: Show “Saved locally” or “Synced” status.
- **Okta SAML**: Integrate for `currentUser`.
- **Auto-Refresh**: Add `setInterval(refreshAnnotations, 30000);`.
- **Partial JSONB Updates**: Implement `PATCH /api/annotations/<id>/`.

---

### Final Notes

- **Restored `localStorage`**: Annotations now save to both `localStorage` (`annotations_<permalink>`) and backend (
  PostgreSQL JSONB).
- **Fixed Saving**: Annotations persist locally on reload, with backend sync when available.
- **Preserved Features**: Sidebar (“Annotate”/“Hide”), highlights, filter, instructions, clear, refresh, export/import.
- **Styling**: MkDocs Material, dark mode, green highlights (`#4caf50`), Nunito Sans unchanged.
- **Backend**: Django ORM, PostgreSQL JSONB, canonicalized URLs, no Okta.
- **Test Thoroughly**: Verify `localStorage` and backend integration, especially offline scenarios.

Please test the updated `index.html` and confirm if annotations save correctly. If you meant `localStorage` only (no
backend) or have specific requirements (e.g., offline UI, sync logic), let me know, and I’ll adjust. Ready for your
feedback!