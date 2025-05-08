Thank you for the request to update the **"Show"** button text to **"Annotate"** in the annotation system’s test page (
`index.html`, artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb`). This change applies to the sidebar toggle button,
which currently toggles between "Show" (when the sidebar is hidden) and "Hide" (when the sidebar is visible). I’ll
modify the button text so it displays **"Annotate"** when the sidebar is hidden and **"Hide"** when the sidebar is
visible, preserving all existing functionality and styling (MkDocs Material theme, dark mode, green highlights, Nunito
Sans font) from our April 26, 2025, work. No changes are needed to the Django backend, PostgreSQL, or Docker setup, as
this is a frontend-only update.

---

### Clarification and Approach

- **Button Context**: The `#sidebar-toggle` button controls the sidebar’s visibility. Its text is set in the
  `updateSidebarVisibility()` function:
    - Sidebar hidden: Button says "Show" (to reveal the sidebar).
    - Sidebar visible: Button says "Hide" (to hide the sidebar).
- **Requested Change**:
    - Change "Show" to **"Annotate"** when the sidebar is hidden.
    - Keep "Hide" when the sidebar is visible.
- **Scope**:
    - Update the JavaScript in `index.html` to set `toggleButton.textContent = 'Annotate'` when `isSidebarVisible` is
      `false`.
    - Preserve all other functionality (sidebar toggle, highlight toggling, multi-user filter, instructions overlay,
      “Clear Annotations,” export/import, “Refresh Annotations”).
    - Maintain styling (MkDocs Material, dark mode, green highlights, Nunito Sans).
    - No changes to Django APIs (`/api/annotations/`), PostgreSQL JSONB, canonicalized URLs, or Docker deployment.
- **Assumptions**:
    - Only the button text changes; no functional or styling changes to the button itself.
    - The term “Annotate” reflects the action of opening the sidebar to view/create annotations.
    - No additional UI changes (e.g., button size, position) unless specified.

**Confirmation**: If you meant a different button (e.g., “Show Instructions”) or want “Annotate” to appear in other
states (e.g., replace “Hide”), please clarify, and I’ll adjust.

---

### Challenges and Considerations

1. **Text Update**:
    - Simple change in `updateSidebarVisibility()`: Replace `toggleButton.textContent = 'Show'` with `'Annotate'`.
    - Ensure the button’s purpose remains clear (“Annotate” suggests opening the sidebar for annotation tasks).
2. **Consistency**:
    - Verify the change doesn’t affect sidebar toggle logic or responsive design.
    - Test in both light and dark modes to ensure text visibility.
3. **No Backend Impact**:
    - Purely a JavaScript change within `index.html`; no impact on Django, PostgreSQL, or APIs.

---

### Updated Artifact

I’ll provide an updated `index.html` (same `artifact_id`) with the button text changed from “Show” to **“Annotate”**
when the sidebar is hidden. The rest of the file (styling, functionality, backend integration) remains identical to the
previous version (April 26, 2025, with MkDocs Material, dark mode, green highlights, Nunito Sans).

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

---

### Changes Made

- **Updated Button Text**:
    - In the `updateSidebarVisibility()` function, changed:
      ```javascript
      toggleButton.textContent = 'Show';
      ```
      to:
      ```javascript
      toggleButton.textContent = 'Annotate';
      ```
    - Now, the button shows:
        - **"Annotate"** when the sidebar is hidden (`isSidebarVisible = false`).
        - **"Hide"** when the sidebar is visible (`isSidebarVisible = true`).
- **Preserved Everything Else**:
    - JavaScript logic (RecogitoJS, `fetch` to Django APIs, event handlers).
    - Styling (MkDocs Material, dark mode, green highlights `#4caf50`, Nunito Sans).
    - Functionality (sidebar toggle, highlight toggling, multi-user filter, instructions, clear, refresh,
      export/import).
    - Backend integration (Django, PostgreSQL JSONB, canonicalized URLs, no Okta).

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

4. **Test the Button Text**:
    - **Initial State**:
        - Sidebar visible (default): `#sidebar-toggle` shows **"Hide"**.
        - Click button: Sidebar hides, button shows **"Annotate"**.
        - Click again: Sidebar reappears, button shows **"Hide"**.
    - **Responsive Design**:
        - Resize to <768px (mobile): Verify button text (“Annotate”/“Hide”) and functionality.
    - **Styling**:
        - Confirm button retains MkDocs Material styling (indigo `#3f51b5` in light mode, green `#4caf50` in dark mode).
        - Check text visibility in light/dark modes.
    - **Functionality**:
        - Test sidebar toggle: Verify annotations highlight (green `#4caf50`) when sidebar is hidden, single highlight
          when clicked in sidebar.
        - Test all features: Create annotations, filter users, open instructions, clear, refresh, export/import.
        - Verify Django API calls (`/api/annotations/`) work.
        - Check PostgreSQL:
          ```sql
          SELECT * FROM annotations;
          ```
          Confirm `permalink`, `user`, `annotation->>'version'`.

---

### How It Works

- **Button Text**:
    - Controlled by `updateSidebarVisibility()`:
      ```javascript
      if (isSidebarVisible) {
          sidebar.classList.remove('hidden');
          toggleButton.textContent = 'Hide';
          // ...
      } else {
          sidebar.classList.add('hidden');
          toggleButton.textContent = 'Annotate';
          // ...
      }
      ```
    - Clicking `#sidebar-toggle` calls `toggleSidebar()`, which flips `isSidebarVisible` and updates the button text.
- **No Impact on Functionality**:
    - Sidebar toggle still shows/hides `#sidebar`, toggles green highlights, and clears active highlights when hidden.
    - All other features (filter, instructions, clear, etc.) are unaffected.
- **Styling**:
    - Button retains Material Design (rounded, hover `scale(1.05)`, Nunito Sans font).
    - Works in light mode (`--button-bg: #3f51b5`) and dark mode (`--button-bg: #4caf50`).
- **Backend**:
    - Django APIs (`/api/annotations/`) handle annotations (PostgreSQL JSONB) with `user`, `permalink`, `timestamp`,
      `version`.
    - Canonicalized URLs (`window.location.origin + pathname`) unchanged.

---

### Limitations and Notes

- **Button Text**: Changed only “Show” to “Annotate”; “Hide” remains as is. If you want “Hide” changed (e.g., to
  “Close”), let me know.
- **Styling**: No visual changes to the button; retains MkDocs Material aesthetic.
- **Scope**: Minimal change to meet your request; no unintended side effects.
- **Context**: Aligns with your April 26, 2025, preferences (Django ORM, PostgreSQL JSONB, canonicalized URLs, no Okta,
  MkDocs Material, dark mode, green highlights, Nunito Sans).

---

### Testing Instructions

1. **Deploy**:
    - Update `static/index.html` with the new artifact.
    - Run `docker-compose up --build` (if not running).
    - Access `http://localhost:8000`.

2. **Test Button Text**:
    - **Sidebar Visible**: Confirm `#sidebar-toggle` shows **“Hide”**.
    - **Sidebar Hidden**: Click button; verify it shows **“Annotate”**.
    - Toggle multiple times; ensure text switches correctly.
    - Check `localStorage` (`sidebarVisible`) persists state.

3. **Test Styling**:
    - Verify button styling (indigo in light mode, green in dark mode, Nunito Sans font).
    - Test hover effect (`scale(1.05)`) and visibility in both modes.
    - Resize to <768px; confirm button text and full-width layout.

4. **Test Functionality**:
    - **Sidebar Toggle**: Verify sidebar shows/hides, green highlights (`#4caf50`) appear when hidden, single highlight
      when clicked.
    - **Annotations**: Create as “Alice”; check PostgreSQL (`SELECT * FROM annotations;`).
    - **Other Features**: Test user filter, instructions, clear, refresh, export/import.
    - **Concurrency**: Use two browsers; verify conflict alerts.
    - **Multi-Page**: Test with `about.html`; confirm separate `permalink` rows.

5. **Test Canonicalized URLs**:
    - Access `http://localhost:8000/index.html?test=1`.
    - Verify `permalink`: `http://localhost:8000/index.html` in PostgreSQL.

---

### Troubleshooting

- **Button Text Incorrect**:
    - Open browser Console; log `toggleButton.textContent` in `updateSidebarVisibility()`.
    - Check `isSidebarVisible` state.
- **Sidebar Not Toggling**:
    - Verify `toggleSidebar()` and `sidebar.classList` logic.
    - Inspect CSS for `#sidebar.hidden`.
- **Styling Issues**:
    - Confirm `--button-bg`, `--button-text` in DevTools.
    - Check light/dark mode switching.
- **Functionality Broken**:
    - Verify JavaScript unchanged except for button text.
    - Check Django API responses (`/api/annotations/`).
- **Provide Details**:
    - Share errors, browser, screenshots, or PostgreSQL logs.

---

### Enhancements (Optional)

From our April 26, 2025, discussions:

- **Okta SAML**: Add for `currentUser` (deferred).
- **Custom Button Text**: Change “Hide” to another term (e.g., “Close”).
- **Styling Tweaks**: Adjust button size, color, or position.
- **Auto-Refresh**: Add `setInterval(refreshAnnotations, 30000);`.
- **Partial JSONB Updates**: Implement `PATCH /api/annotations/<id>/` for `body`.
- **More Material Features**: Add navbar, search, or collapsible sidebar.

---

### Final Notes

- Updated `#sidebar-toggle` to show **“Annotate”** (hidden) and **“Hide”** (visible).
- Preserved all functionality (sidebar, highlights, filter, instructions, clear, refresh, export/import).
- Maintained styling (MkDocs Material, dark mode, green highlights `#4caf50`, Nunito Sans).
- No changes to Django ORM, PostgreSQL JSONB, canonicalized URLs, or Docker.
- Test the updated `index.html` and let me know if you need further tweaks (e.g., “Hide” text, additional styling, or
  backend enhancements). Ready for your feedback!