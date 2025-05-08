Thank you for confirming that we’ll keep the **Django ORM** with **PostgreSQL JSONB** for the annotation system, as it
aligns well with your requirements for structure, concurrency, and multi-page support. Your final request is to style
the test page (`index.html`, artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb`) to use a theme inspired by **MkDocs
Material**, incorporating **dark mode**, **green highlights** for annotations, and the **Nunito Sans** Google Font. This
builds on our previous work (April 26, 2025), maintaining all functionality (sidebar toggle, highlight toggling,
multi-user filter, instructions overlay, “Clear Annotations,” export/import) while enhancing the visual design.

Below, I’ll outline the approach to update the styling of `index.html` to match the MkDocs Material aesthetic, add dark
mode, use green highlights, and apply Nunito Sans. I’ll preserve the existing functionality and backend (Django,
PostgreSQL, canonicalized URLs, no Okta) and provide an updated `index.html` artifact with the requested styling.

---

### Requirements Clarification

Based on your request and the context of our prior work, here’s what you want to achieve:

1. **MkDocs Material Theme**:
    - Style `index.html` to resemble **MkDocs Material**, a popular documentation theme known for its clean, modern
      design, responsive layout, and polished typography.
    - Key features to emulate:
        - Minimalist layout with a sidebar and content area.
        - Smooth transitions and hover effects.
        - Responsive design for mobile devices.
        - Professional typography and spacing.
    - Use Material Design principles (e.g., shadows, rounded corners, consistent padding).

2. **Dark Mode**:
    - Implement a **dark mode** toggle, similar to MkDocs Material’s theme switcher.
    - Default to light mode, with a button to switch to dark mode (persisted via `localStorage`).
    - Dark mode should adjust background, text, and UI element colors to a dark palette (e.g., dark gray background,
      light text).

3. **Green Highlights**:
    - Change annotation highlights from yellow (`rgba(255, 255, 0, 0.3)`) to **green** (e.g., a vibrant green like
      `#4caf50` with transparency).
    - Ensure highlights are visible in both light and dark modes.
    - Apply to:
        - All annotations when the sidebar is closed.
        - The active annotation when clicked in the sidebar (open state).

4. **Nunito Sans Google Font**:
    - Use **Nunito Sans** (via Google Fonts) for all text (body, headings, buttons, inputs, etc.).
    - Apply appropriate weights (e.g., 400 for body, 700 for headings) for hierarchy.

5. **Preserve Functionality**:
    - Retain all existing features from `index.html`:
        - Sidebar toggle (show/hide).
        - Highlight toggling (all green highlights when sidebar closed, one highlighted when clicked).
        - Multi-user filter (select users to view annotations).
        - Instructions overlay (explains annotation creation, highlighting, toggling).
        - “Clear Annotations” (deletes all annotations for the current permalink in PostgreSQL).
        - Export/import annotations as JSON.
        - “Refresh Annotations” button for syncing.
    - Ensure compatibility with Django backend (REST APIs at `/api/annotations/`).
    - Maintain responsive design (mobile-friendly, as in the original `<768px` media query).

6. **Assumptions**:
    - **MkDocs Material Inspiration**: Use a simplified version of the theme (e.g., colors, typography, layout) without
      directly including the full MkDocs Material CSS/JS (to keep `index.html` lightweight and static).
    - **Dark Mode Toggle**: Add a button in the sidebar controls (next to “Clear Annotations,” “Refresh,” etc.) to
      toggle light/dark mode.
    - **Green Highlights**: Use a green shade like `#4caf50` (Material Design green) with 30% opacity for visibility.
    - **Nunito Sans**: Import via Google Fonts CDN with weights 400 (regular) and 700 (bold).
    - **No Backend Changes**: Styling is frontend-only; no changes to Django, PostgreSQL, or Docker setup.
    - **Canonicalized URLs**: Continue using `window.location.origin + pathname` for permalinks.
    - **No Okta**: Use `#user-input` for `currentUser`.

**Questions** (answered based on context):

- **MkDocs Material Scope**: Emulate the aesthetic (colors, layout, transitions) without the full framework, as
  `index.html` is a static page.
- **Dark Mode Persistence**: Store preference in `localStorage`, like sidebar visibility.
- **Green Shade**: Use `#4caf50` (adjustable if you prefer a different green).
- **Font Weights**: 400 for body, 700 for headings/buttons, unless you specify otherwise.
- **Toggle Placement**: Add dark mode button in `#controls` for accessibility.

If you have specific preferences (e.g., exact green hex code, different toggle placement, or additional Material
features like a top navbar), please clarify, and I’ll adjust.

---

### Challenges and Considerations

1. **MkDocs Material Aesthetic**:
    - MkDocs Material uses a complex CSS/JS framework with features like palette switching, search, and navigation. For
      a static `index.html`, we’ll replicate key visual elements (colors, typography, sidebar, transitions) using custom
      CSS.
    - Color palette (inspired by Material Design):
        - Light mode: White background (`#ffffff`), dark text (`#333`), primary color (`#3f51b5` for buttons).
        - Dark mode: Dark background (`#121212`), light text (`#e0e0e0`), accent color (`#4caf50` for highlights).
    - Use CSS variables for easy theme switching.

2. **Dark Mode Implementation**:
    - Add a toggle button that switches a `data-theme` attribute on `<html>`.
    - Use CSS variables to adjust colors based on `data-theme="light"` or `data-theme="dark"`.
    - Persist choice in `localStorage` to maintain user preference across page reloads.
    - Ensure green highlights are visible in both modes (e.g., adjust opacity or use a lighter green in dark mode).

3. **Green Highlights**:
    - Replace yellow highlights (`rgba(255, 255, 0, 0.3)`) with green (`rgba(76, 175, 80, 0.3)` for `#4caf50`).
    - Ensure active highlights (when sidebar is open) are distinct (e.g., solid green border).
    - Test visibility on both light and dark backgrounds.

4. **Nunito Sans**:
    - Import via Google Fonts: `https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;700`.
    - Apply globally with fallback to `sans-serif`.
    - Adjust font sizes and weights for hierarchy (e.g., larger for headings, bold for comments).

5. **Responsive Design**:
    - Preserve existing media query (`@media (max-width: 768px)`) for mobile layout.
    - Ensure Material-inspired design (e.g., sidebar, buttons) adapts to small screens.
    - Test toggle button and overlay readability on mobile.

6. **Lightweight Approach**:
    - Avoid heavy dependencies (e.g., full Material Design Components library) to keep `index.html` static and fast.
    - Use vanilla CSS/JS for theming, leveraging RecogitoJS for annotations.

---

### Proposed Approach

1. **MkDocs Material Styling**:
    - **Layout**: Keep flexbox layout (`body`, `#content`, `#sidebar`) with a fixed sidebar and toggle button, mimicking
      Material’s sidebar.
    - **Colors**:
        - Light mode: White background, dark gray text (`#333`), indigo buttons (`#3f51b5`).
        - Dark mode: Dark gray background (`#121212`), light text (`#e0e0e0`), green accents (`#4caf50`).
    - **Typography**: Use Nunito Sans (400, 700) for all text.
    - **UI Elements**: Rounded buttons, subtle shadows, hover transitions (e.g., `transform: scale(1.05)`).
    - **Sidebar**: Fixed, scrollable, with Material-like padding and card-style annotation comments.

2. **Dark Mode**:
    - Add a toggle button in `#controls` (e.g., “Toggle Theme”).
    - Use `data-theme` on `<html>` to switch between light/dark CSS variables:
      ```css
      :root[data-theme="light"] {
          --background: #ffffff;
          --text: #333333;
      }
      :root[data-theme="dark"] {
          --background: #121212;
          --text: #e0e0e0;
      }
      ```
    - Persist in `localStorage` (e.g., `theme: 'dark'`).
    - Adjust green highlights for dark mode (e.g., `rgba(76, 175, 80, 0.4)` for better contrast).

3. **Green Highlights**:
    - Update `.r6o-annotation` and `.active-highlight`:
      ```css
      .r6o-annotation {
          background: rgba(76, 175, 80, 0.3);
      }
      .no-highlights .r6o-annotation.active-highlight {
          background: rgba(76, 175, 80, 0.4);
          border: 1px solid #4caf50;
      }
      ```
    - Ensure no highlights when sidebar is open (except active).

4. **Nunito Sans**:
    - Import Google Fonts in `<head>`:
      ```html
      <link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;700&display=swap" rel="stylesheet">
      ```
    - Apply globally:
      ```css
      body {
          font-family: 'Nunito Sans', sans-serif;
      }
      ```

5. **Preserve Functionality**:
    - Keep all JavaScript logic (RecogitoJS, `fetch` to Django APIs, event handlers).
    - Ensure CSS changes don’t break sidebar toggle, highlight toggling, or responsive behavior.
    - Test with Django backend (`/api/annotations/`) and PostgreSQL.

6. **Responsive Design**:
    - Update media query to align with Material’s mobile-friendly design (stacked layout, full-width sidebar).
    - Ensure buttons and inputs are touch-friendly.

---

### Updated Artifact

I’ll provide an updated `index.html` (same `artifact_id` as before) with the new styling. No changes are needed to the
Django backend, PostgreSQL schema, or Docker setup, as this is a frontend-only update.

#### Updated `index.html`

- Applies MkDocs Material-inspired styling (colors, layout, transitions).
- Adds dark mode toggle with `localStorage` persistence.
- Uses green highlights (`#4caf50`).
- Sets Nunito Sans font (400, 700).
- Preserves all functionality (sidebar, highlights, filter, instructions, clear, refresh, export/import).

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

### Setup Instructions

Since this is a frontend-only update, no changes are needed to the Django backend, PostgreSQL schema, or Docker setup
from our April 26, 2025, artifacts. To apply the styling:

1. **Update `index.html`**:
    - Replace `static/index.html` with the above artifact.
    - Ensure it’s in the `static/` directory of your Django project:
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

4. **Test the Styling**:
    - **Visuals**: Verify MkDocs Material-inspired layout (clean sidebar, rounded buttons, shadows).
    - **Dark Mode**:
        - Click “Toggle Theme” in `#controls`.
        - Confirm background changes to dark (`#121212`), text to light (`#e0e0e0`).
        - Reload page; verify theme persists via `localStorage`.
    - **Green Highlights**:
        - Create an annotation; check green highlight (`#4caf50`, 30% opacity).
        - Close sidebar; verify all annotations highlighted.
        - Open sidebar, click an annotation; confirm single green highlight (40% opacity, solid border).
    - **Nunito Sans**:
        - Inspect text (e.g., via browser DevTools); confirm `font-family: 'Nunito Sans', sans-serif`.
        - Verify weights (400 for body, 700 for headings/comments).
    - **Responsive Design**:
        - Resize browser to <768px or use mobile device.
        - Confirm stacked layout, full-width sidebar, touch-friendly buttons.
    - **Functionality**:
        - Test all features: create annotations, toggle sidebar, filter users, open instructions, clear annotations,
          refresh, export/import.
        - Verify Django API calls (`/api/annotations/`) work.
        - Check PostgreSQL:
          ```sql
          SELECT * FROM annotations;
          ```
          Confirm `permalink`, `user`, `annotation->>'version'`.

---

### How It Works

- **MkDocs Material Styling**:
    - **Layout**: Flexbox with fixed sidebar, rounded corners, and shadows mimic Material’s clean design.
    - **Colors**: Light mode uses white (`#ffffff`), indigo buttons (`#3f51b5`); dark mode uses dark gray (`#121212`),
      green buttons (`#4caf50`).
    - **Typography**: Nunito Sans (400, 700) for all text, with hierarchy (e.g., `font-weight: 700` for `.comment`).
    - **Transitions**: Smooth hover effects (`transform: scale(1.05)`) and theme switching (
      `transition: background 0.3s`).

- **Dark Mode**:
    - Toggled via `#theme-toggle`, updating `data-theme` on `<html>`.
    - CSS variables (`--background`, `--text`, etc.) adjust colors.
    - Persisted in `localStorage` (`theme: 'light'` or `'dark'`).
    - Green highlights adjusted for dark mode (40% opacity for better contrast).

- **Green Highlights**:
    - `.r6o-annotation`: `rgba(76, 175, 80, 0.3)` for all highlights.
    - `.active-highlight`: `rgba(76, 175, 80, 0.4)` with `#4caf50` border when sidebar is open.
    - No highlights when sidebar is open (except active), per original logic.

- **Nunito Sans**:
    - Imported via Google Fonts CDN.
    - Applied globally: `body { font-family: 'Nunito Sans', sans-serif; }`.
    - Weights: 400 for body/inputs, 700 for headings/buttons/comments.

- **Functionality**:
    - JavaScript unchanged (RecogitoJS, `fetch` to Django APIs, event handlers).
    - CSS ensures compatibility with sidebar toggle, highlight toggling, and responsive layout.
    - Django backend handles annotations (PostgreSQL, JSONB) as before.

---

### Limitations and Notes

- **MkDocs Material Scope**: Simplified to CSS variables and custom styles, not the full MkDocs framework, to keep
  `index.html` static and lightweight.
- **Dark Mode**: Uses `data-theme` and CSS variables; no external libraries for minimal overhead.
- **Green Highlights**: `#4caf50` chosen for Material Design alignment; can adjust (e.g., `#388e3c` for darker green) if
  preferred.
- **Nunito Sans**: Weights 400/700; additional weights (e.g., 300, 900) can be added if needed.
- **Responsive Design**: Enhanced for mobile, but complex Material features (e.g., collapsible sidebar) omitted for
  simplicity.
- **No Backend Changes**: Styling is isolated to `index.html`; Django, PostgreSQL, Docker unchanged.

---

### Testing Instructions

1. **Deploy**:
    - Update `static/index.html` with the new artifact.
    - Run `docker-compose up --build` (if not running).
    - Access `http://localhost:8000`.

2. **Test Styling**:
    - **MkDocs Material**:
        - Verify clean layout (sidebar, content, rounded corners, shadows).
        - Check button hover effects (`scale(1.05)`).
    - **Dark Mode**:
        - Toggle theme; confirm color changes (light: white bg, dark: `#121212`).
        - Reload; verify persistence.
    - **Green Highlights**:
        - Create annotation; check green highlight in content.
        - Toggle sidebar; verify all/single highlight behavior.
    - **Nunito Sans**:
        - Inspect font in DevTools; confirm Nunito Sans, weights 400/700.
    - **Responsive**:
        - Resize to <768px; confirm stacked layout, touch-friendly controls.

3. **Test Functionality**:
    - Create annotations as “Alice”; verify in PostgreSQL.
    - Test sidebar toggle, user filter, instructions, clear, refresh, export/import.
    - Confirm concurrency (two browsers, conflict alert).
    - Test multi-page (e.g., `about.html`).

4. **Test Canonicalized URLs**:
    - Access `http://localhost:8000/index.html?test=1`.
    - Verify `permalink`: `http://localhost:8000/index.html` in PostgreSQL.

---

### Troubleshooting

- **Styling Issues**:
    - Check browser Console for CSS errors.
    - Inspect elements to confirm `--background`, `--text`, etc.
- **Dark Mode Not Persisting**:
    - Verify `localStorage` in DevTools (`theme` key).
    - Log `toggleTheme()` execution.
- **Highlights Not Visible**:
    - Inspect `.r6o-annotation` styles; confirm `rgba(76, 175, 80, 0.3)`.
    - Test in both light/dark modes.
- **Font Not Loading**:
    - Check network tab for Google Fonts request.
    - Confirm `<link>` in `<head>`.
- **Functionality Broken**:
    - Verify JavaScript unchanged from prior version.
    - Check Django API responses (`/api/annotations/`).
- **Provide Details**:
    - Share errors, browser, screenshots, or PostgreSQL logs.

---

### Enhancements (Optional)

Drawing from our April 26, 2025, discussions:

- **Okta SAML**:
    - Add for `currentUser` (deferred, but can integrate later).
- **Custom Green**:
    - Adjust highlight color (e.g., `#388e3c`) if `#4caf50` isn’t ideal.
- **More Material Features**:
    - Add top navbar, search, or collapsible sidebar (requires more JS/CSS).
- **Font Weights**:
    - Include additional Nunito Sans weights (e.g., 300, 900).
- **Auto-Refresh**:
    - `setInterval(refreshAnnotations, 30000);` for real-time updates.
- **Partial JSONB Updates**:
    - Add `PATCH /api/annotations/<id>/` for `body` updates.

---

### Final Notes

- The updated `index.html` applies **MkDocs Material** styling, **dark mode**, **green highlights** (`#4caf50`), and *
  *Nunito Sans** font.
- All functionality is preserved (sidebar, highlights, filter, instructions, clear, refresh, export/import).
- **Django ORM** and **PostgreSQL JSONB** remain unchanged, supporting annotations with `user`, `timestamp`,
  `permalink`.
- **Canonicalized URLs** and **no Okta** align with your April 26, 2025, preferences.
- **Docker** deployment is unaffected.

Please test the updated `index.html` and let me know if the styling meets your expectations or if you need adjustments (
e.g., different green, more Material features, or backend changes). If you want to revisit Okta or add enhancements, I’m
ready to iterate!