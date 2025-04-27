Thank you for the update! I understand you’d like to revert from using Amazon S3 to **PostgreSQL** for storing
annotations, as discussed in our previous conversations, and incorporate specific requirements for the annotation
structure. This makes sense, especially for robust concurrency handling and structured data management in a
multi-editor, multi-page scenario. You’re concerned about ensuring annotations are uniquely identified, timestamped, and
associated with a page’s permalink to support multiple pages across sites. Let’s integrate these requirements into the
existing `index.html` (artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb`) while preserving all features (sidebar,
highlight toggling, multi-user filter, instructions overlay, and “Clear Annotations”).

Your request builds on our prior work and aligns with discussions about structured data storage (e.g., the Django app
with PostgreSQL on April 20, 2025). Below, I’ll clarify the requirements, propose an approach using PostgreSQL, and
provide an updated `index.html` that integrates with a PostgreSQL backend via a minimal server (since static HTML alone
can’t directly query PostgreSQL). I’ll also address the new annotation requirements (user, timestamp, permalink) and
ensure compatibility with multiple pages and editors.

---

### Clarification of Requirements

Based on your request and our previous work, here’s what you want to achieve:

1. **Revert to PostgreSQL Storage**:
    - Replace `localStorage` (or the S3 approach from our last session) with PostgreSQL for storing annotations.
    - Store annotations in a **JSONB** column to allow flexible updates to the annotation structure.
    - Reference our earlier PostgreSQL discussions (e.g., April 20, 2025, for the Django contact manager app), adapting
      the setup for annotations.

2. **Annotation Structure**:
    - **Unique Identifier**: Include the **user** (from `#user-input` or authentication) as part of the annotation’s
      unique identifier to distinguish annotations by different editors.
    - **Timestamp**: Add a timestamp to each annotation to track creation or update time, used in the JSONB structure
      for versioning or conflict resolution.
    - **Permalink Association**: Associate each annotation with the **fully qualified permalink** of the page (e.g.,
      `https://example.com/index.html`) to bundle annotations by page, supporting multiple pages from multiple sites.

3. **Multi-Editor and Multi-Page Support**:
    - Handle **multiple editors** concurrently editing annotations for the same page without conflicts.
    - Support **multiple pages** (e.g., `index.html`, `about.html`) across different sites (e.g., `example.com`,
      `anothersite.com`), with annotations grouped by permalink.
    - Ensure annotations are stored and retrieved correctly for each page.

4. **Preserve Existing Features**:
    - Retain all functionality from `index.html`:
        - Sidebar toggle (show/hide).
        - Highlight toggling (all highlights on when sidebar closed, one highlighted when sidebar open via click).
        - Multi-user filter (select users to view their annotations).
        - Instructions overlay (explains annotation creation, highlighting, toggling).
        - “Clear Annotations” (removes all annotations for the page).
        - Export/import annotations as JSON.
    - Update “Clear Annotations” to delete annotations from PostgreSQL for the current page.

5. **Concurrency and JSONB Updates**:
    - Use PostgreSQL’s **JSONB** column to store the annotation’s JSON structure (e.g., RecogitoJS format with `id`,
      `body`, `target`, `creator`).
    - Allow partial updates to the JSONB structure (e.g., update `body` or `version` without overwriting the entire
      annotation).
    - Handle concurrency (e.g., multiple editors saving annotations) using PostgreSQL’s transaction isolation or
      optimistic locking (via timestamp).

6. **Static Site with Backend**:
    - The frontend remains a static `index.html`, but a minimal backend (e.g., Flask or Django) is needed to handle
      PostgreSQL queries, as static HTML can’t directly connect to a database.
    - Host the backend and frontend together (e.g., via Docker, as in our April 20, 2025, Django setup).
    - Use REST APIs to communicate between the frontend (`index.html`) and backend (PostgreSQL).

**Assumptions** (please confirm or clarify):

- **Backend Framework**: Use **Flask** for simplicity (lighter than Django) to handle PostgreSQL queries, unless you
  prefer Django (as in our April 20, 2025, discussions).
- **Database Schema**:
    - Table: `annotations`.
    - Columns:
        - `id`: Primary key (auto-incremented).
        - `user`: String (from `#user-input` or auth), part of the unique identifier.
        - `permalink`: String (e.g., `https://example.com/index.html`), to group annotations by page.
        - `annotation`: JSONB, storing the RecogitoJS annotation (e.g.,
          `{ "id": "anno-1", "body": [...], "target": {...}, "creator": {...} }`).
        - `timestamp`: Timestamp with time zone, for creation/update tracking and concurrency.
        - `version`: String (e.g., ISO timestamp), embedded in the JSONB for conflict detection.
    - Unique constraint: `(user, permalink, annotation->>'id')` to ensure each user’s annotation ID is unique per page.
- **Permalink**: Derived from `window.location.href` (e.g.,
  `https://<bucket>.s3-website-<region>.amazonaws.com/index.html` or `http://localhost:8000/index.html`).
- **Authentication**: No Okta/SAML (as in the last session); use the user name from `#user-input` for simplicity, unless
  you want to reintegrate authentication.
- **Concurrency**: Use the `timestamp` and `version` in JSONB for optimistic locking (check if the stored version is
  older before updating).
- **Multi-Page Bundling**: Filter annotations by `permalink` in PostgreSQL queries to load only the current page’s
  annotations.
- **Clear Annotations**: Deletes all annotations for the current `permalink` in PostgreSQL.
- **Deployment**: Use Docker (as in April 20, 2025) with a Flask backend, PostgreSQL, and static `index.html` served via
  a web server (e.g., Gunicorn/Nginx).

**Questions** (optional, to refine the solution):

1. **Backend Preference**: Flask or Django? Flask is lighter for this use case, but Django aligns with our prior
   PostgreSQL work.
2. **Authentication**: Should we use Okta SAML (as in the last session) to set `currentUser`, or rely on `#user-input`?
3. **Permalink Format**: Is `window.location.href` sufficient, or do you need a custom format (e.g., canonical URL)?
4. **Concurrency Needs**: How many editors (e.g., 2–5 vs. 10+)? Is optimistic locking (timestamp/version) enough, or do
   you need stricter transaction isolation?
5. **JSONB Updates**: Which parts of the annotation JSONB need partial updates (e.g., `body`, `creator`, or custom
   fields)?
6. **Multi-Site Setup**: Are pages hosted on different domains (e.g., `example.com` vs. `anothersite.com`), or within
   one domain (e.g., S3 bucket)?
7. **Clear Annotations Scope**: Delete all annotations for the `permalink`, or only the current user’s?

For now, I’ll assume:

- **Flask Backend**: Minimal REST API for PostgreSQL queries.
- **No Authentication**: Use `#user-input` for `currentUser`.
- **Permalink**: `window.location.href`.
- **Concurrency**: Optimistic locking with `timestamp` and `version` for 2–5 editors.
- **JSONB Updates**: Allow updating `body` and `version` in JSONB.
- **Multi-Site**: Pages on different domains; bundle by `permalink`.
- **Clear Annotations**: Deletes all annotations for the `permalink`.
- **Docker Deployment**: Flask, PostgreSQL, and static `index.html`.

If these don’t align, please clarify, and I’ll adjust.

---

### Challenges and Considerations

1. **PostgreSQL vs. S3**:
    - PostgreSQL offers structured storage, transactions, and JSONB for flexible updates, unlike S3’s file-based
      approach.
    - Requires a backend (Flask), adding complexity compared to S3’s client-side AWS SDK.
    - Better for concurrency (transactions, locking) and querying (e.g., filter by `permalink`).

2. **Annotation Structure**:
    - **User in Identifier**: Combine `user`, `permalink`, and annotation `id` for uniqueness.
    - **Timestamp**: Store in the table (`timestamp`) and JSONB (`version`) for creation/update tracking.
    - **Permalink**: Store as a column to group annotations; ensures multi-page support.

3. **Concurrency**:
    - Use optimistic locking: Check `version` before updating; prompt user to refresh if a newer version exists.
    - PostgreSQL’s transaction isolation can prevent conflicts for simultaneous writes.
    - Low concurrency (2–5 editors) makes optimistic locking sufficient.

4. **JSONB Updates**:
    - JSONB allows partial updates (e.g., `annotation->'body' = new_body`) without overwriting the entire object.
    - Store RecogitoJS annotation JSON (e.g., `{ "id": "anno-1", "body": [...], "target": {...} }`) in the `annotation`
      column.

5. **Static Site with Backend**:
    - Static `index.html` uses `fetch` to call Flask API endpoints (e.g., `/annotations` for load/save).
    - Flask handles PostgreSQL queries and returns JSON responses.
    - Docker simplifies deployment (Flask + PostgreSQL).

6. **Multi-Page Support**:
    - Filter annotations by `permalink` in PostgreSQL queries.
    - Ensure `permalink` is unique and consistent across page loads.

---

### Proposed Approach

Here’s how we’ll implement PostgreSQL storage with the new annotation requirements:

1. **PostgreSQL Schema**:
    - Table: `annotations`
    - Columns:
        - `id`: Serial (primary key).
        - `user`: Varchar (e.g., “Alice” from `#user-input`).
        - `permalink`: Varchar (e.g., `https://example.com/index.html`).
        - `annotation`: JSONB (RecogitoJS annotation with `id`, `body`, `target`, `creator`, `version`).
        - `timestamp`: Timestamp with time zone (creation/update time).
    - Unique constraint: `(user, permalink, annotation->>'id')`.
    - Index: On `permalink` for fast filtering.

2. **Flask Backend**:
    - Create a minimal Flask app with REST APIs:
        - `GET /annotations?permalink=<url>`: Load annotations for the page.
        - `POST /annotations`: Save or update an annotation.
        - `DELETE /annotations/<id>`: Delete an annotation.
        - `DELETE /annotations?permalink=<url>`: Clear all annotations for the page.
    - Use `psycopg2` for PostgreSQL queries.
    - Handle JSONB updates with SQL (e.g., `UPDATE annotations SET annotation = jsonb_set(...)`).
    - Implement optimistic locking (check `version` before updates).

3. **Annotation Structure**:
    - JSONB content:
      ```json
      {
        "id": "anno-1",
        "body": [{ "value": "Great point!", "purpose": "commenting" }],
        "target": { "selector": [{ "type": "TextQuoteSelector", "exact": "sample paragraph" }, { "type": "TextPositionSelector", "start": 20, "end": 35 }] },
        "creator": { "type": "Person", "name": "Alice" },
        "version": "2025-04-26T18:37:00Z"
      }
      ```
    - Unique identifier: `(user, permalink, annotation->>'id')`.
    - Timestamp: Stored in `timestamp` column and `version` field (ISO 8601).

4. **Frontend Updates**:
    - Replace `localStorage` with `fetch` calls to Flask APIs.
    - Get `permalink` from `window.location.href`.
    - Add `version` to annotations for concurrency.
    - Update `saveAnnotation` to check for conflicts (compare `version`).
    - Add a “Refresh Annotations” button to reload annotations.
    - Preserve all features (sidebar, highlights, filter, instructions, clear).

5. **Concurrency**:
    - Check `version` before saving; if newer, alert user to refresh.
    - Use PostgreSQL transactions for atomic updates.
    - Refresh button syncs changes from other editors.

6. **Docker Deployment**:
    - Docker Compose with:
        - Flask app (serves API and static `index.html`).
        - PostgreSQL database.
    - Based on our April 20, 2025, Django setup, adapted for Flask.

7. **No Authentication**:
    - Use `#user-input` for `currentUser` (no Okta/SAML for simplicity).
    - Can reintegrate Okta if needed.

---

### Updated Artifacts

I’ll provide:

- **Updated `index.html`**: Frontend with `fetch` calls to Flask APIs, preserving all features.
- **Flask `app.py`**: Backend with PostgreSQL queries and REST APIs.
- **Docker Compose**: For deployment.
- **SQL Schema**: For PostgreSQL setup.

Since you requested changes to the annotation storage, I’ll use the same `artifact_id` (
`96200c6f-b303-426e-9559-95ac0eebd8bb`) for `index.html` and create new artifacts for `app.py`, `docker-compose.yml`,
and `schema.sql`.

#### 1. Updated `index.html`

- Replaces `localStorage`/S3 with `fetch` calls to Flask APIs.
- Adds `permalink` and `version` to annotations.
- Includes “Refresh Annotations” button.
- Preserves all features.

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

    // Update currentUser when input changes
    userInput.addEventListener('input', () => {
        currentUser = userInput.value.trim();
        localStorage.setItem('currentUser', currentUser);
    });

    // Toggle sidebar visibility and highlights
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

    // Handle toggle button click
    toggleButton.addEventListener('click', toggleSidebar);

    // Handle instructions button click
    instructionsButton.addEventListener('click', () => {
        instructionsOverlay.classList.remove('hidden');
    });

    // Load annotations from PostgreSQL
    async function loadAnnotations() {
        try {
            const permalink = window.location.href;
            const response = await fetch(`/annotations?permalink=${encodeURIComponent(permalink)}`);
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

    // Save annotation to PostgreSQL
    async function saveAnnotation(annotation) {
        try {
            const permalink = window.location.href;
            const version = new Date().toISOString();
            const updatedAnnotation = {
                ...annotation,
                creator: {
                    type: 'Person',
                    name: currentUser || 'Anonymous'
                },
                version: version
            };
            const response = await fetch('/annotations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: currentUser, permalink, annotation: updatedAnnotation })
            });
            if (!response.ok) {
                const error = await response.json();
                if (error.message.includes('conflict')) {
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

    // Fetch annotations (helper)
    async function fetchAnnotations() {
        const permalink = window.location.href;
        const response = await fetch(`/annotations?permalink=${encodeURIComponent(permalink)}`);
        if (!response.ok) throw new Error('Failed to fetch annotations');
        return await response.json();
    }

    // Update user filter dropdown
    function updateUserFilter(annotations) {
        const userFilter = document.getElementById('user-filter');
        const creators = [...new Set(annotations.map(a => a.creator?.name || 'Unknown'))];
        const allUsersOption = '<option value="">All Users</option>';
        const options = creators.map(creator => `<option value="${creator}">${creator}</option>`).join('');
        userFilter.innerHTML = allUsersOption + options;
    }

    // Update sidebar with annotations
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

    // Clear annotations from PostgreSQL
    async function clearAnnotations() {
        try {
            const permalink = window.location.href;
            const response = await fetch(`/annotations?permalink=${encodeURIComponent(permalink)}`, {
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
                    const permalink = window.location.href;
                    for (const annotation of annotations) {
                        const version = new Date().toISOString();
                        const updatedAnnotation = { ...annotation, version };
                        await fetch('/annotations', {
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
            const response = await fetch(`/annotations/${annotation.id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user: currentUser, permalink: window.location.href })
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

#### 2. Flask Backend (`app.py`)

- Handles PostgreSQL queries via REST APIs.
- Supports JSONB updates and optimistic locking.

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import Json
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.getenv('POSTGRES_DB', 'annotations'),
    user=os.getenv('POSTGRES_USER', 'user'),
    password=os.getenv('POSTGRES_PASSWORD', 'password'),
    host=os.getenv('POSTGRES_HOST', 'db')
)
cursor = conn.cursor()

# Ensure table exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS annotations (
        id SERIAL PRIMARY KEY,
        user VARCHAR(255) NOT NULL,
        permalink VARCHAR(2048) NOT NULL,
        annotation JSONB NOT NULL,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user, permalink, (annotation->>'id'))
    );
    CREATE INDEX IF NOT EXISTS idx_permalink ON annotations (permalink);
""")
conn.commit()


@app.route('/annotations', methods=['GET'])
def get_annotations():
    permalink = request.args.get('permalink')
    if not permalink:
        return jsonify({'error': 'Permalink required'}), 400
    cursor.execute("SELECT annotation FROM annotations WHERE permalink = %s", (permalink,))
    annotations = [row[0] for row in cursor.fetchall()]
    return jsonify(annotations)


@app.route('/annotations', methods=['POST'])
def save_annotation():
    data = request.get_json()
    user = data.get('user', 'Anonymous')
    permalink = data.get('permalink')
    annotation = data.get('annotation')
    if not (user and permalink and annotation):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check for conflicts
    cursor.execute(
        "SELECT annotation->>'version' FROM annotations WHERE user = %s AND permalink = %s AND annotation->>'id' = %s",
        (user, permalink, annotation['id'])
    )
    existing = cursor.fetchone()
    if existing and existing[0] > annotation.get('version'):
        return jsonify({'error': 'Version conflict'}), 409

    # Upsert annotation
    cursor.execute("""
        INSERT INTO annotations (user, permalink, annotation, timestamp)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (user, permalink, (annotation->>'id'))
        DO UPDATE SET annotation = EXCLUDED.annotation, timestamp = CURRENT_TIMESTAMP
        RETURNING annotation
    """, (user, permalink, Json(annotation)))
    conn.commit()
    return jsonify(cursor.fetchone()[0])


@app.route('/annotations/<id>', methods=['DELETE'])
def delete_annotation(id):
    data = request.get_json()
    user = data.get('user', 'Anonymous')
    permalink = data.get('permalink')
    if not (user and permalink):
        return jsonify({'error': 'Missing required fields'}), 400
    cursor.execute(
        "DELETE FROM annotations WHERE user = %s AND permalink = %s AND annotation->>'id' = %s",
        (user, permalink, id)
    )
    conn.commit()
    return jsonify({'success': True})


@app.route('/annotations', methods=['DELETE'])
def clear_annotations():
    permalink = request.args.get('permalink')
    if not permalink:
        return jsonify({'error': 'Permalink required'}), 400
    cursor.execute("DELETE FROM annotations WHERE permalink = %s", (permalink,))
    conn.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### 3. Docker Compose (`docker-compose.yml`)

- Sets up Flask, PostgreSQL, and Nginx for static files.

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
  app:
    image: python:3.13-slim
    command: gunicorn -w 4 -b 0.0.0.0:5000 app:app
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

#### 4. Dockerfile

- Builds the Flask app and Nginx.

```dockerfile
FROM nginx:alpine
COPY static /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### 5. Nginx Configuration (`nginx.conf`)

- Proxies API requests to Flask, serves static files.

```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
    location /annotations {
        proxy_pass http://app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 6. PostgreSQL Schema (`schema.sql`)

- Defines the `annotations` table.

```sql
CREATE TABLE IF NOT EXISTS annotations (
    id SERIAL PRIMARY KEY,
    user VARCHAR(255) NOT NULL,
    permalink VARCHAR(2048) NOT NULL,
    annotation JSONB NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user, permalink, (annotation->>'id'))
);
CREATE INDEX IF NOT EXISTS idx_permalink ON annotations (permalink);
```

---

### Setup Instructions

1. **Directory Structure**:
   ```
   project/
   ├── static/
   │   └── index.html
   ├── app.py
   ├── docker-compose.yml
   ├── Dockerfile
   ├── nginx.conf
   └── schema.sql
   ```

2. **Install Docker**:
    - Ensure Docker and Docker Compose are installed.

3. **Build and Run**:
    - Save all files in the `project/` directory.
    - Run:
      ```bash
      docker-compose up --build
      ```
    - Access the site at `http://localhost:8000`.

4. **Initialize Database**:
    - Connect to PostgreSQL:
      ```bash
      docker exec -it <container-name> psql -U user -d annotations
      ```
    - Run `schema.sql`:
      ```sql
      \i /path/to/schema.sql
      ```

5. **Test the App**:
    - Open `http://localhost:8000` in a browser.
    - Enter a user name (e.g., “Alice”) in `#user-input`.
    - Create an annotation; check PostgreSQL:
      ```sql
      SELECT * FROM annotations;
      ```
    - Verify `user`, `permalink`, `timestamp`, and `annotation->>'version'`.
    - Test highlight toggling, filter, instructions, clear, and refresh.
    - Test multi-page:
        - Copy `index.html` to `about.html`, access `http://localhost:8000/about.html`.
        - Create annotations; verify separate rows with different `permalink`.

6. **Test Concurrency**:
    - Open two browsers (e.g., Chrome, Firefox).
    - Create annotations as “Alice” and “Bob”; verify unique rows.
    - Update the same annotation; check for conflict alert.
    - Click “Refresh Annotations” to sync changes.

---

### How It Works

- **Annotation Storage**:
    - Annotations are stored in PostgreSQL’s `annotations` table.
    - Example row:
      ```sql
      id: 1
      user: 'Alice'
      permalink: 'http://localhost:8000/index.html'
      annotation: { "id": "anno-1", "body": [...], "creator": {"name": "Alice"}, "version": "2025-04-26T18:37:00Z" }
      timestamp: '2025-04-26 18:37:00+00'
      ```
    - Unique constraint ensures `(user, permalink, annotation->>'id')` is unique.

- **Frontend**:
    - `index.html` uses `fetch` to call Flask APIs.
    - `permalink` is `window.location.href`.
    - `version` is added to annotations for concurrency.
    - “Refresh Annotations” reloads annotations.

- **Backend**:
    - Flask handles CRUD operations:
        - `GET /annotations`: Filters by `permalink`.
        - `POST /annotations`: Inserts or updates with optimistic locking.
        - `DELETE /annotations/<id>`: Deletes by `user`, `permalink`, `id`.
        - `DELETE /annotations`: Clears by `permalink`.
    - JSONB allows partial updates (e.g., `annotation->'body'`).

- **Concurrency**:
    - Checks `version` before saving; alerts if newer version exists.
    - Transactions ensure atomic updates.

- **Multi-Page**:
    - Annotations are grouped by `permalink`.
    - Supports pages like `index.html`, `about.html` on different domains.

---

### Limitations and Notes

- **Backend Requirement**: Flask is needed for PostgreSQL; static `index.html` alone can’t query databases.
- **Authentication**: Uses `#user-input`; Okta can be added if needed.
- **Concurrency**: Optimistic locking works for low concurrency; high concurrency may need stricter isolation.
- **Permalink**: Assumes `window.location.href`; may need canonicalization for consistency.
- **JSONB Updates**: Currently updates entire `annotation`; can add endpoints for partial updates (e.g., `body` only).

---

### Testing Instructions

1. **Deploy**:
    - Run `docker-compose up --build`.
    - Access `http://localhost:8000`.

2. **Test Annotations**:
    - Create annotation as “Alice”; verify in PostgreSQL.
    - Update/delete; check `timestamp` and `version`.
    - Clear annotations; confirm empty table for `permalink`.

3. **Test Concurrency**:
    - Create annotations in two browsers.
    - Update same annotation; verify conflict alert.
    - Refresh to sync changes.

4. **Test Multi-Page**:
    - Add `about.html`; create annotations.
    - Verify separate `permalink` rows in PostgreSQL.

5. **Test Features**:
    - Toggle sidebar/highlights, filter users, open instructions, export/import.
    - Ensure all work with PostgreSQL.

6. **Responsive Design**:
    - Test on mobile (<768px); verify UI and functionality.

---

### Troubleshooting

- **API Errors**:
    - Check Flask logs (`docker logs <app-container>`).
    - Verify `POSTGRES_*` environment variables.
- **Annotations Not Saving**:
    - Inspect `fetch` responses in browser Console.
    - Check PostgreSQL logs (`docker logs <db-container>`).
- **Concurrency Conflicts**:
    - Add `console.log` in `saveAnnotation` to debug `version`.
- **Permalink Issues**:
    - Log `window.location.href`; ensure consistency across browsers.
- **Provide Details**:
    - Share errors, browser, PostgreSQL logs, or table contents.

---

### Enhancements (Optional)

Drawing from our April 20, 2025, discussions (e.g., Django, Docker):

- **Authentication**: Add Okta SAML (as in last session) for `currentUser`.
- **Auto-Refresh**:
  ```javascript
  setInterval(refreshAnnotations, 30000);
  ```
- **Partial JSONB Updates**:
    - Add endpoint: `PATCH /annotations/<id>` to update `body`.
- **Django Backend**:
    - Convert to Django for consistency with prior work.
- **Permalink Normalization**:
    - Canonicalize URLs (e.g., remove query params).

---

### Final Notes

- The solution reverts to **PostgreSQL** with a **Flask** backend, using **JSONB** for annotations.
- Annotations include **user**, **timestamp** (`version`), and **permalink** for uniqueness and multi-page support.
- All features are preserved, with a “Refresh Annotations” button for syncing.
- **Docker** simplifies deployment, based on our April 20, 2025, setup.
- **Concurrency** is handled via optimistic locking.

Please test the artifacts and let me know if they meet your needs or if you need adjustments (e.g., Django instead of
Flask, Okta integration, or different concurrency handling). If you have more ideas, I’m ready to keep iterating!