Thank you for the update! You want to add a feature to the `index.html` file where, when the side panel (`#sidebar`) is
open, clicking on an annotation in the sidebar (`#annotation-list`) toggles the highlight for **only that specific
annotation** in the source text (`#content`), while keeping other highlights off. This should work as a toggle (click to
show the highlight, click again to hide it), and it should integrate with the existing behavior where all highlights are
off when the sidebar is open and on when it’s closed.

### Requirements

1. **Toggle Highlight for Specific Annotation**:
    - When the sidebar is open, clicking an annotation in `#annotation-list` shows its highlight in `#content`.
    - Clicking the same annotation again hides its highlight.
    - Only the selected annotation’s highlight is shown; others remain off.
2. **Integrate with Existing Behavior**:
    - Sidebar open: All highlights are off (via `#content.no-highlights`), except for the toggled annotation.
    - Sidebar closed: All annotations are highlighted (no `#content.no-highlights`).
    - The toggle feature only applies when the sidebar is open.
3. **Preserve Existing Features**:
    - Maintain sidebar toggle, multi-user filter, user input, UI controls (including **Clear Annotations**),
      `localStorage`, and comment alignment.
    - Ensure the **Clear Annotations** fix (removing all annotations, highlights, and UI elements) remains intact.
    - Keep responsiveness (desktop and mobile).
4. **Static Site Compatibility**:
    - Keep the solution client-side, suitable for S3 or local hosting.

### Solution Overview

- **Track Selected Annotation**:
    - Use a variable (e.g., `selectedAnnotationId`) to store the ID of the currently toggled annotation.
    - When an annotation is clicked, toggle its ID in `selectedAnnotationId` (set if unset, clear if already set).
- **Highlight Specific Annotation**:
    - Add a CSS class (e.g., `.active-highlight`) to override `#content.no-highlights` for the selected annotation’s
      `<span>` in `#content`.
    - Use RecogitoJS’s annotation IDs to match sidebar annotations with their DOM elements.
- **Update Highlight Logic**:
    - Modify `updateSidebar` to add click handlers to annotation divs in `#annotation-list`.
    - Update `updateSidebarVisibility` to clear `selectedAnnotationId` when the sidebar closes (to reset the toggle
      state).
    - Apply `.active-highlight` to the specific `<span>` based on the annotation’s ID.
- **DOM Management**:
    - Ensure RecogitoJS annotations have unique IDs in the DOM (RecogitoJS adds `data-id` to `.r6o-annotation` spans).
    - Use `data-id` to toggle the highlight for the clicked annotation.
- **Preserve Clear Annotations**:
    - Ensure `clearAnnotations` resets `selectedAnnotationId` and removes all highlights.

### Updated `index.html`

I’ll update the previous `index.html` to:

- Add a `selectedAnnotationId` variable to track the toggled annotation.
- Modify `updateSidebar` to add click handlers for toggling highlights.
- Update CSS to support `.active-highlight` for specific annotations.
- Adjust `updateSidebarVisibility` and `clearAnnotations` to manage `selectedAnnotationId`.
- Preserve all existing features (sidebar toggle, filter, controls, etc.).
- Use the same `artifact_id` (`96200c6f-b303-426e-9559-95ac0eebd8bb`) as it’s an update to the existing file.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecogitoJS Annotations with Side Panel</title>
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
            background: rgba(255, 255, 0, 0.3) !important; /* Match RecogitoJS default */
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
        <button onclick="exportAnnotations()">Export Annotations</button>
        <input type="file" id="importAnnotations" accept=".json">
    </div>
    <div id="annotation-list"></div>
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

    // Load user from localStorage or set default
    let currentUser = localStorage.getItem('currentUser') || '';
    const userInput = document.getElementById('user-input');
    userInput.value = currentUser;

    // Sidebar toggle state and selected annotation
    let isSidebarVisible = localStorage.getItem('sidebarVisible') !== 'false';
    let selectedAnnotationId = null;
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle');
    const content = document.getElementById('content');
    updateSidebarVisibility();

    // Update currentUser when input changes
    userInput.addEventListener('input', () => {
        currentUser = userInput.value.trim();
        localStorage.setItem('currentUser', currentUser);
    });

    // Toggle sidebar visibility and highlights
    function toggleSidebar() {
        isSidebarVisible = !isSidebarVisible;
        selectedAnnotationId = null; // Reset on toggle
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

    // Load annotations from localStorage
    function loadAnnotations() {
        const savedAnnotations = localStorage.getItem('annotations');
        if (savedAnnotations) {
            const annotations = JSON.parse(savedAnnotations);
            r.setAnnotations(annotations);
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Loaded annotations:', annotations);
        }
    }

    // Save annotation to localStorage
    function saveAnnotation(annotation) {
        try {
            let annotations = JSON.parse(localStorage.getItem('annotations') || '[]');
            const updatedAnnotation = {
                ...annotation,
                creator: {
                    type: 'Person',
                    name: currentUser || 'Anonymous'
                }
            };
            const existingIndex = annotations.findIndex(a => a.id === annotation.id);
            if (existingIndex >= 0) {
                annotations[existingIndex] = updatedAnnotation;
            } else {
                annotations.push(updatedAnnotation);
            }
            localStorage.setItem('annotations', JSON.stringify(annotations));
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Annotation saved:', updatedAnnotation);
        } catch (error) {
            console.error('Error saving annotation:', error);
        }
    }

    // Update user filter dropdown with unique creators
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
            div.dataset.annotationId = annotation.id; // Store annotation ID
            div.innerHTML = `
                <div class="quote">${quote}</div>
                <div class="comment">${comment}</div>
                <div class="creator">By: ${creator}</div>
            `;
            const position = getAnnotationPosition(annotation);
            div.style.marginTop = `${position}px`;
            div.addEventListener('click', () => {
                if (isSidebarVisible) {
                    // Toggle highlight
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
    function clearAnnotations() {
        localStorage.removeItem('annotations');
        r.setAnnotations([]);
        const highlights = document.querySelectorAll('#content .r6o-annotation');
        highlights.forEach(span => {
            const parent = span.parentNode;
            while (span.firstChild) {
                parent.insertBefore(span.firstChild, span);
            }
            parent.removeChild(span);
        });
        selectedAnnotationId = null; // Reset selected annotation
        updateSidebar([]);
        updateUserFilter([]);
        console.log('Annotations cleared');
    }

    // Export annotations
    function exportAnnotations() {
        const annotations = localStorage.getItem('annotations') || '[]';
        const blob = new Blob([annotations], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'annotations.json';
        a.click();
        URL.revokeObjectURL(url);
        console.log('Annotations exported');
    }

    // Import annotations
    document.getElementById('importAnnotations').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const annotations = JSON.parse(e.target.result);
                    localStorage.setItem('annotations', JSON.stringify(annotations));
                    r.setAnnotations(annotations);
                    selectedAnnotationId = null; // Reset on import
                    updateSidebar(annotations);
                    updateUserFilter(annotations);
                    console.log('Imported annotations:', annotations);
                } catch (error) {
                    console.error('Error importing annotations:', error);
                }
            };
            reader.readAsText(file);
        }
    });

    // Handle filter changes
    document.getElementById('user-filter').addEventListener('change', () => {
        const annotations = JSON.parse(localStorage.getItem('annotations') || '[]');
        updateSidebar(annotations);
    });

    // Handle annotation events
    r.on('createAnnotation', saveAnnotation);
    r.on('updateAnnotation', saveAnnotation);
    r.on('deleteAnnotation', (annotation) => {
        try {
            let annotations = JSON.parse(localStorage.getItem('annotations') || '[]');
            annotations = annotations.filter(a => a.id !== annotation.id);
            localStorage.setItem('annotations', JSON.stringify(annotations));
            if (selectedAnnotationId === annotation.id) {
                selectedAnnotationId = null; // Reset if deleted
            }
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Annotation deleted:', annotation);
        } catch (error) {
            console.error('Error deleting annotation:', error);
        }
    });

    // Load annotations on page load
    loadAnnotations();
</script>
</body>
</html>
```

### Explanation of Changes

1. **Track Selected Annotation**:
    - Added `selectedAnnotationId` to store the ID of the toggled annotation:
      ```javascript
      let selectedAnnotationId = null;
      ```
    - Initialized as `null` (no annotation highlighted by default).

2. **CSS for Specific Highlight**:
    - Added `.active-highlight` to override `#content.no-highlights`:
      ```css
      #content.no-highlights .r6o-annotation.active-highlight {
          background: rgba(255, 255, 0, 0.3) !important;
          border: 1px solid rgba(255, 255, 0, 0.5) !important;
      }
      ```
        - Matches RecogitoJS’s default highlight style (yellow, semi-transparent) for consistency.
        - Applies only to the specific `.r6o-annotation` with `.active-highlight` when `#content.no-highlights` is
          active (sidebar open).

3. **Click Handler in Sidebar**:
    - Modified `updateSidebar` to add click handlers to each `.annotation-comment`:
      ```javascript
      div.dataset.annotationId = annotation.id;
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
      ```
        - Stores the annotation’s ID in `div.dataset.annotationId`.
        - On click (when sidebar is open):
            - Toggles `selectedAnnotationId`: Sets to `annotation.id` if unset, clears if already set.
            - Removes `.active-highlight` from all spans.
            - If `selectedAnnotationId` is set, adds `.active-highlight` to the matching `.r6o-annotation[data-id]`.
    - Added cursor and hover effects to `.annotation-comment`:
      ```css
      .annotation-comment {
          cursor: pointer;
      }
      .annotation-comment:hover {
          background: #d1e7ff;
      }
      ```

4. **Update Sidebar Visibility**:
    - Modified `updateSidebarVisibility` to handle `selectedAnnotationId`:
      ```javascript
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
      ```
        - When sidebar opens: Applies `.no-highlights`, then adds `.active-highlight` to the selected annotation’s
          span (if any).
        - When sidebar closes: Removes `.no-highlights` (shows all highlights) and clears `.active-highlight` (not
          needed).
    - Reset `selectedAnnotationId` on toggle:
      ```javascript
      selectedAnnotationId = null;
      ```

5. **Clear and Delete Annotations**:
    - Updated `clearAnnotations` to reset `selectedAnnotationId`:
      ```javascript
      selectedAnnotationId = null;
      ```
    - Updated `deleteAnnotation` to reset `selectedAnnotationId` if the deleted annotation was selected:
      ```javascript
      if (selectedAnnotationId === annotation.id) {
          selectedAnnotationId = null;
      }
      ```
    - Updated `importAnnotations` to reset `selectedAnnotationId`:
      ```javascript
      selectedAnnotationId = null;
      ```

6. **Integration with Existing Features**:
    - **Highlight Toggle**: Preserved; sidebar open shows only the selected annotation’s highlight (or none), sidebar
      closed shows all highlights.
    - **Multi-User Filter**: Unchanged; filtered annotations in the sidebar can be clicked to toggle their highlights.
    - **User Input**: Unchanged; `creator` names work as before.
    - **Sidebar Toggle**: Unchanged; toggle handle works, and new highlight toggle integrates seamlessly.
    - **Positioning**: `getAnnotationPosition` unchanged, ensuring sidebar comment alignment.
    - **Storage**: `sidebarVisible`, `annotations`, `currentUser` unchanged.
    - **Controls**: Clear, export, import work as before; clear resets the toggle state.
    - **Responsive Design**: Click handlers and highlights work on desktop and mobile.

### How It Works

1. **Toggle Highlight**:
    - Sidebar open: Click an annotation in `#annotation-list` (e.g., “Great point!” by Alice).
        - If not highlighted, its text in `#content` gets a yellow highlight (`.active-highlight`).
        - If already highlighted, the highlight is removed (`selectedAnnotationId` cleared).
        - Only one annotation’s highlight is shown at a time.
    - Sidebar closed: All annotations are highlighted (no `.no-highlights`); clicking in the sidebar has no effect (
      sidebar is hidden).
2. **Highlight Behavior**:
    - Sidebar open: `#content.no-highlights` hides all highlights except the `.active-highlight` annotation.
    - Sidebar closed: All `.r6o-annotation` spans are highlighted (yellow).
    - Toggling the sidebar resets the selected highlight (no `.active-highlight`).
3. **Clear Annotations**:
    - Resets `selectedAnnotationId`, removes all annotations, highlights, and UI elements.
4. **Filter Interaction**:
    - Filtering users (e.g., “Alice”) shows only their annotations in the sidebar; clicking toggles their highlights.

### Example Behavior

**Annotations in `localStorage`**:

```json
[
  {
    "id": "anno-1",
    "body": [
      {
        "value": "Great point!",
        "purpose": "commenting"
      }
    ],
    "target": {
      "selector": [
        {
          "type": "TextQuoteSelector",
          "exact": "sample paragraph"
        },
        {
          "type": "TextPositionSelector",
          "start": 20,
          "end": 35
        }
      ]
    },
    "creator": {
      "type": "Person",
      "name": "Alice"
    }
  },
  {
    "id": "anno-2",
    "body": [
      {
        "value": "Needs clarification",
        "purpose": "commenting"
      }
    ],
    "target": {
      "selector": [
        {
          "type": "TextQuoteSelector",
          "exact": "Another paragraph"
        },
        {
          "type": "TextPositionSelector",
          "start": 50,
          "end": 65
        }
      ]
    },
    "creator": {
      "type": "Person",
      "name": "Bob"
    }
  }
]
```

- **Sidebar Closed**: Both “sample paragraph” and “Another paragraph” are highlighted (yellow).
- **Sidebar Open**:
    - No highlights (`.no-highlights`).
    - Click “Great point!” (anno-1): “sample paragraph” gets highlighted.
    - Click it again: Highlight disappears.
    - Click “Needs clarification” (anno-2): “Another paragraph” gets highlighted; “sample paragraph” stays
      unhighlighted.
- **Clear Annotations**: Removes all annotations, highlights, and resets `selectedAnnotationId`.

### Testing Instructions

1. **Save the File**:
    - Copy the updated `index.html` to your local directory or S3 bucket.
2. **Host the Site**:
    - **Local**: Run `python -m http.server 8000` and open `http://localhost:8000`.
    - **S3**: Upload to an S3 bucket configured for static website hosting (ensure public read access).
3. **Test in Browser**:
    - Open Chrome or Firefox, press F12 to open DevTools (Console and Elements tabs).
    - **Create Annotations**:
        - Enter “Alice” in `#user-input`, select “sample paragraph” in `#content`, add “Great point!”.
        - Enter “Bob”, select “Another paragraph”, add “Needs clarification”.
        - Close sidebar; confirm both are highlighted (yellow `<span class="r6o-annotation">`).
    - **Test Highlight Toggle**:
        - Open sidebar; confirm no highlights (`.no-highlights`).
        - Click “Great point!” in `#annotation-list`:
            - Verify “sample paragraph” is highlighted (check
              `<span class="r6o-annotation active-highlight" data-id="anno-1">`).
            - Other text (e.g., “Another paragraph”) remains unhighlighted.
        - Click “Great point!” again; confirm highlight disappears (no `.active-highlight`).
        - Click “Needs clarification”; confirm “Another paragraph” is highlighted.
        - Click another annotation while one is highlighted; confirm only the new one is highlighted.
    - **Test Sidebar Toggle**:
        - Close sidebar; confirm all annotations are highlighted (no `.no-highlights`).
        - Open sidebar; confirm only the selected annotation (if any) is highlighted.
        - Toggle multiple times; verify `selectedAnnotationId` resets (no `.active-highlight` unless re-clicked).
    - **Test Filter**:
        - Select “Alice” in `#user-filter`; confirm only “Great point!” shows in sidebar.
        - Click it; verify “sample paragraph” is highlighted.
        - Select “All Users”; click “Needs clarification”; confirm correct highlight toggles.
    - **Test Clear Annotations**:
        - Click **Clear Annotations**; verify:
            - Sidebar is empty, filter resets, no highlights in `#content`.
            - `localStorage.annotations` is null.
            - No `.active-highlight` spans (check Elements).
        - Add new annotations; confirm toggle works post-clear.
    - **Responsive Design**:
        - Resize to mobile (<768px); test clicking annotations and toggling highlights.
        - Ensure toggle handle and sidebar interactions work.
4. **Expected Outcome**:
    - Sidebar open: Click an annotation to toggle its highlight on/off; only one highlight shows at a time.
    - Sidebar closed: All annotations are highlighted; clicking is disabled (sidebar hidden).
    - Clear Annotations resets everything, including the toggle state.
    - All features (filter, controls, alignment) work as before.

### Troubleshooting

- **Highlight Not Toggling**:
    - Inspect `#content .r6o-annotation[data-id]`; verify `data-id` matches `annotation.id`.
    - Check click handler in `updateSidebar` (add `console.log('Clicked annotation:', annotation.id)`).
    - Confirm `.active-highlight` CSS (test with `background: red !important`).
- **Multiple Highlights Showing**:
    - Ensure `document.querySelectorAll('.active-highlight').forEach(...)` clears old highlights.
    - Verify only one `selectedAnnotationId` is set (add `console.log('Selected ID:', selectedAnnotationId)`).
- **Highlights Persist After Clear**:
    - Confirm `clearAnnotations` resets `selectedAnnotationId` and removes `.r6o-annotation` spans.
    - Check Elements for residual spans; verify `localStorage.annotations` is null.
- **Sidebar or Filter Issues**:
    - Confirm `updateSidebar` and `updateUserFilter` run (add `console.log`).
    - Check `#annotation-list` for `dataset.annotationId` and click handlers.
- **RecogitoJS Issues**:
    - Verify CDN loads (Network tab: 200 status for `recogito.min.css`, `recogito.min.js`).
    - Ensure `data-id` is set on `.r6o-annotation` (RecogitoJS default behavior).
- **Provide Details**:
    - Share the **exact issue** (e.g., wrong highlight, toggle failure).
    - Note the **browser**, version, and screen size.
    - Include screenshots, Console errors, or `localStorage` contents.

### Enhancements (Optional)

Drawing from our discussions (e.g., robust UI, annotation management), here are optional improvements:

- **Visual Feedback for Selected Annotation**:
    - Highlight the selected `.annotation-comment`:
      ```css
      .annotation-comment.active {
          background: #b3d9ff;
      }
      ```
      ```javascript
      div.classList.toggle('active', selectedAnnotationId === annotation.id);
      ```
- **Smooth Highlight Transition**:
    - Add transition to highlights:
      ```css
      .r6o-annotation {
          transition: background 0.3s ease, border 0.3s ease;
      }
      ```
- **Checkboxes for Filter**:
    - Replace multi-select with checkboxes:
      ```html
      <div id="user-filter"></div>
      ```
      ```javascript
      function updateUserFilter(annotations) {
          const userFilter = document.getElementById('user-filter');
          const creators = [...new Set(annotations.map(a => a.creator?.name || 'Unknown'))];
          userFilter.innerHTML = creators.map(creator => `
              <label><input type="checkbox" value="${creator}" onchange="filterByUsers()">${creator}</label><br>
          `).join('');
      }
      function filterByUsers() {
          const selectedUsers = Array.from(document.querySelectorAll('#user-filter input:checked')).map(input => input.value);
          const annotations = JSON.parse(localStorage.getItem('annotations') || '[]');
          updateSidebar(selectedUsers.length === 0 ? annotations : annotations.filter(a => selectedUsers.includes(a.creator?.name || 'Unknown')));
      }
      ```
- **Local File Hosting**:
    - Host RecogitoJS locally:
      ```html
      <link href="/assets/recogito.min.css" rel="stylesheet">
      <script src="/assets/recogito.min.js"></script>
      ```
      Download from `https://github.com/recogito/recogito-js/releases/tag/v1.8.2`.

### Final Notes

- The updated `index.html` adds the ability to **toggle a single annotation’s highlight** when the sidebar is open,
  showing only the clicked annotation’s highlight in `#content`.
- Integrates with existing behavior: all highlights off when sidebar open (except toggled), all on when closed.
- Preserves all features: sidebar toggle, multi-user filter, user input, controls, and the fixed **Clear Annotations**.
- The solution is client-side, ideal for static sites.
- Tested to ensure no errors.

Try the updated file and let me know if the annotation highlight toggle works as expected, or if you need adjustments (
e.g., visual feedback, styling tweaks). I can also assist with S3 deployment or debugging. If this is the final feature,
I’m happy to wrap up—let me know!