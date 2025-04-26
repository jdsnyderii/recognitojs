The error you’re encountering in the `index.html` file is:

```
Global fetch network error: TypeError: URL is not valid or contains user credentials.
Error saving annotation:
```

This stems from the invalid placeholder URL (`https://<api-id>.execute-api.<region>.amazonaws.com/prod/annotations`)used
in the `fetch` call to save RecogitoJS annotations to an AWS API Gateway and Aurora PostgreSQL database. Since you’ve
requested to fix this by replacing the database and API Gateway storage with a **local storage option**, I’ll modify the
`index.html` to save annotations to the browser’s `localStorage` instead. This approach is ideal for a static HTML site,
as it eliminates server-side dependencies, avoids the invalid URL error, and persists annotations client-side.

### Solution Overview

- **Remove the `fetch` Call**: Eliminate the API Gateway request causing the `TypeError` due to the invalid URL.
- **Use `localStorage`**: Save annotations to the browser’s `localStorage`, which stores key-value pairs persistently in
  the user’s browser.
- **Update `index.html`**: Modify the `createAnnotation` handler to store annotations in `localStorage` and add a
  `loadAnnotations` function to retrieve them on page load.
- **Maintain RecogitoJS Functionality**: Ensure annotations are created, saved, and loaded correctly using the W3C Web
  Annotation format.

**Benefits**:

- Fixes the `TypeError` by removing the invalid URL.
- Works entirely client-side, perfect for static sites hosted on S3 or local servers.
- Persists annotations across page reloads in the user’s browser.
- Simplifies setup by removing AWS dependencies.

**Limitations**:

- `localStorage` is limited to ~5-10MB (varies by browser), sufficient for thousands of annotations but not for
  large-scale use.
- Annotations are stored per-browser, not shared across devices or users (unlike a database).
- No server-side persistence or collaboration features.

### Updated `index.html` with Local Storage

I’ll update the `index.html` to:

- Use the corrected RecogitoJS CDN URLs (`@recogito/recogito-js@1.8.2`).
- Remove the `fetch` call and placeholder URL.
- Store annotations in `localStorage` on `createAnnotation`.
- Load existing annotations from `localStorage` on page load.
- Keep the `<div>` element and remove `mode: 'pre'` (as fixed previously).

Here’s the updated file:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecogitoJS Annotations</title>
    <link href="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.js"></script>
</head>
<body>
<div id="content">Text to annotate.</div>
<script>
    // Initialize RecogitoJS
    const r = Recogito.init({
        content: document.getElementById('content')
    });

    // Load annotations from localStorage on page load
    function loadAnnotations() {
        const savedAnnotations = localStorage.getItem('annotations');
        if (savedAnnotations) {
            const annotations = JSON.parse(savedAnnotations);
            r.loadAnnotations(annotations);
            console.log('Loaded annotations:', annotations);
        }
    }

    // Save annotation to localStorage
    r.on('createAnnotation', (annotation) => {
        try {
            // Get existing annotations or initialize empty array
            let annotations = JSON.parse(localStorage.getItem('annotations')) || [];
            // Update or add the new annotation
            const existingIndex = annotations.findIndex(a => a.id === annotation.id);
            if (existingIndex >= 0) {
                annotations[existingIndex] = annotation; // Update existing
            } else {
                annotations.push(annotation); // Add new
            }
            // Save back to localStorage
            localStorage.setItem('annotations', JSON.stringify(annotations));
            console.log('Annotation saved:', annotation);
        } catch (error) {
            console.error('Error saving annotation:', error);
        }
    });

    // Load annotations when the page loads
    loadAnnotations();
</script>
</body>
</html>
```

**Changes Made**:

- **Removed API Gateway Code**:
    - Deleted the `apiUrl` constant and the `fetch` call, eliminating the `TypeError` caused by the invalid URL.
- **Added Local Storage Logic**:
    - In the `createAnnotation` handler:
        - Retrieve existing annotations from `localStorage` (key: `annotations`) or initialize an empty array.
        - Check if the annotation’s `id` already exists to update it (handles edits) or append new annotations.
        - Save the updated array back to `localStorage` as a JSON string.
    - Implemented `loadAnnotations`:
        - Reads the `annotations` key from `localStorage`.
        - Parses the JSON and loads annotations into RecogitoJS using `r.loadAnnotations()`.
        - Called on page load to restore annotations.
- **Kept Previous Fixes**:
    - Correct CDN URLs (`@recogito/recogito-js@1.8.2`).
    - No `mode: 'pre'` to avoid the earlier `TypeError` with `<div>`.
- **Error Handling**:
    - Retained `try/catch` to handle potential `localStorage` errors (e.g., quota exceeded or JSON parsing issues).
- **Logging**:
    - Added `console.log` for debugging saved and loaded annotations.

**Artifact ID**:

- Used the same `artifact_id` (`96200c6f-b303-426e-9559-95ac0eebd8bb`) as the previous `index.html`, as this is an
  update to the same file.

### How It Works

1. **Annotation Creation**:
    - When you select text in the `<div id="content">` and create an annotation (e.g., highlight and comment),
      RecogitoJS triggers the `createAnnotation` event.
    - The handler adds or updates the annotation in the `annotations` array in `localStorage`.
    - The annotation is stored in W3C Web Annotation JSON format (e.g.,
      `{ "id": "anno-123", "body": [{ "value": "Comment" }], "target": {...} }`).
2. **Annotation Persistence**:
    - `localStorage` saves the annotations as a JSON string under the key `annotations`.
    - Annotations persist in the browser across page reloads until cleared (e.g., via `localStorage.clear()`).
3. **Annotation Loading**:
    - On page load, `loadAnnotations()` retrieves the `annotations` key, parses the JSON, and passes it to
      `r.loadAnnotations()`.
    - RecogitoJS renders the saved annotations on the page.

### Testing the Fix

1. **Save the Updated File**:
    - Copy the updated `index.html` to your local directory or S3 bucket.
2. **Host the Site**:
    - **Local**: Run `python -m http.server 8000` and open `http://localhost:8000`.
    - **S3**: Upload to an S3 bucket configured for static website hosting (ensure public read access or appropriate
      permissions).
3. **Test in Browser**:
    - Open Chrome or Firefox, press F12 to open DevTools, and go to the **Console** tab.
    - Select text in the `<div id="content">`, create an annotation (e.g., highlight and add a comment), and save it.
    - Check the **Console** for output like `Annotation saved: { id: "anno-123", ... }`.
    - Refresh the page and verify the annotation reappears, with `Loaded annotations: [...]` in the console.
    - Open DevTools > **Application** > **Local Storage** > `http://localhost:8000` (or your S3 URL) and confirm the
      `annotations` key contains a JSON array of annotations.
4. **Expected Outcome**:
    - No `TypeError: URL is not valid or contains user credentials`.
    - Annotations are saved to `localStorage` and persist across page reloads.
    - No network requests (since `fetch` is removed).

### Example `localStorage` Content

After creating an annotation, `localStorage.getItem('annotations')` might look like:

```json
[
  {
    "@context": "http://www.w3.org/ns/anno.jsonld",
    "id": "anno-123",
    "type": "Annotation",
    "body": [
      {
        "value": "This is a comment",
        "purpose": "commenting"
      }
    ],
    "target": {
      "selector": {
        "type": "TextQuoteSelector",
        "exact": "Text to annotate"
      }
    }
  }
]
```

### Additional Considerations

- **Storage Limits**:
    - `localStorage` typically allows 5-10MB per origin (browser-dependent: Chrome ~10MB, Firefox ~10MB, Safari ~5MB).
    - A single annotation is ~1-2KB, so you can store thousands before hitting limits.
    - If the quota is exceeded, the `try/catch` will log an error (e.g., `QuotaExceededError`). You can add a check:
      ```javascript
      if (annotations.length > 1000) {
          console.warn('Approaching localStorage limit; consider clearing old annotations.');
      }
      ```
- **Clearing Annotations**:
    - To reset annotations, add a button or script:
      ```javascript
      function clearAnnotations() {
          localStorage.removeItem('annotations');
          r.loadAnnotations([]);
          console.log('Annotations cleared');
      }
      ```
      Add a button in HTML:
      ```html
      <button onclick="clearAnnotations()">Clear Annotations</button>
      ```
- **Exporting Annotations**:
    - To allow users to download annotations, add an export function:
      ```javascript
      function exportAnnotations() {
          const annotations = localStorage.getItem('annotations') || '[]';
          const blob = new Blob([annotations], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'annotations.json';
          a.click();
          URL.revokeObjectURL(url);
      }
      ```
      Add a button:
      ```html
      <button onclick="exportAnnotations()">Export Annotations</button>
      ```
- **Importing Annotations**:
    - To load annotations from a JSON file, add an input element:
      ```html
      <input type="file" id="importAnnotations" accept=".json">
      ```
      And script:
      ```javascript
      document.getElementById('importAnnotations').addEventListener('change', (event) => {
          const file = event.target.files[0];
          if (file) {
              const reader = new FileReader();
              reader.onload = (e) => {
                  try {
                      const annotations = JSON.parse(e.target.result);
                      localStorage.setItem('annotations', JSON.stringify(annotations));
                      r.loadAnnotations(annotations);
                      console.log('Imported annotations:', annotations);
                  } catch (error) {
                      console.error('Error importing annotations:', error);
                  }
              };
              reader.readAsText(file);
          }
      });
      ```
- **Browser Compatibility**:
    - `localStorage` and RecogitoJS 1.8.2 work in modern browsers (Chrome, Firefox, Safari, Edge).
    - If testing in private/incognito mode, `localStorage` may be restricted (test in a regular browser window).
- **Security**:
    - `localStorage` is per-origin, so annotations are only accessible to your site’s domain.
    - No sensitive data is stored, but avoid storing user-identifiable information in annotations without encryption.

### If You Want to Revert to Database Storage Later

If you decide to use AWS API Gateway and Aurora PostgreSQL later, you can:

- Deploy the API Gateway and Lambda function (per the earlier response).
- Update the `index.html` to restore the `fetch` call with your real API Gateway URL.
- I can provide a modified version with both `localStorage` and database options (e.g., fallback to `localStorage` if
  the API fails).

### Troubleshooting

If you encounter issues with the updated code:

- **No Annotations Saved**:
    - Check the **Console** for errors (e.g., `QuotaExceededError` if `localStorage` is full).
    - Verify `localStorage` in DevTools > **Application** > **Local Storage**.
- **Annotations Not Loading**:
    - Ensure `loadAnnotations()` runs on page load (it’s called in the script).
    - Check if `localStorage.getItem('annotations')` returns valid JSON.
- **RecogitoJS Errors**:
    - Confirm the CDN URLs load correctly (Network tab: 200 status for `recogito.min.css` and `recogito.min.js`).
    - If errors persist, switch to local files (download from
      `https://github.com/recogito/recogito-js/releases/tag/v1.8.2`).
- **Provide Details**:
    - Share the **exact error message** and stack trace (DevTools > Console).
    - Confirm the **browser** and version.
    - Note if you’re testing locally or on S3.

### Final Notes

- The `TypeError: URL is not valid or contains user credentials` is fixed by removing the invalid `fetch` call and using
  `localStorage`.
- The updated `index.html` saves annotations client-side, persisting them across reloads without server dependencies.
- You can enhance the setup with clear, export, or import features (as outlined above) for better user experience.
- The artifact retains the same `artifact_id` (`96200c6f-b303-426e-9559-95ac0eebd8bb`) as it’s an update to the same
  file.

Test the updated file and let me know if it works or if you need additional features (e.g., export/import buttons,
`localStorage` quota management, or help reverting to AWS). I can also provide a version with UI controls or debug any
new issues!
