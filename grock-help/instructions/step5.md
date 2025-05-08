The error you’re encountering when saving an annotation in your RecogitoJS `index.html` file is:

```
Global fetch network error: TypeError: URL is not valid or contains user credentials.
Error saving annotation:
```

This error originates from the `fetch` call in the `createAnnotation` event handler, indicating that the URL provided to
`fetch` is invalid or malformed. Let’s diagnose the cause, focusing on the relevant code, and provide a fix tailored to
your static HTML site setup, which integrates RecogitoJS with an AWS API Gateway endpoint for storing annotations in
Aurora PostgreSQL.

### Relevant Code from `index.html`

From the provided `index.html`:

```javascript
// API Gateway endpoint (replace with your real URL)
const apiUrl = 'https://<api-id>.execute-api.<region>.amazonaws.com/prod/annotations';

// Save annotation to Aurora via API Gateway
r.on('createAnnotation', async (annotation) => {
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(annotation)
        });
        const result = await response.json();
        console.log('Annotation saved:', result);
    } catch (error) {
        console.error('Error saving annotation:', error);
    }
});
```

The error occurs during the `fetch(apiUrl, ...)` call, and the message suggests that `apiUrl` is not a valid URL. The
current `apiUrl` is set to:

```
https://<api-id>.execute-api.<region>.amazonaws.com/prod/annotations
```

This is a placeholder, which explains the issue.

### Diagnosis

The `TypeError: URL is not valid or contains user credentials` typically occurs when the `fetch` API receives a URL
that:

- Is not a syntactically valid URL (e.g., contains unescaped characters, placeholders, or invalid syntax).
- Includes user credentials (e.g., `https://user:password@host.com`), which `fetch` rejects for security reasons.
- Is empty, undefined, or not a string.

In this case, the root cause is the **placeholder URL**:

- The `apiUrl` contains `<api-id>` and `<region>`, which are not valid URL components (angle brackets are not allowed in
  URLs).
- When `fetch` tries to parse `https://<api-id>.execute-api.<region>.amazonaws.com/prod/annotations`, it fails because
  `<api-id>` and `<region>` make the URL syntactically invalid, triggering the `TypeError`.

**Why It Happens on First Save**:

- The `fetch` call is only executed when an annotation is created (via the `createAnnotation` event).
- On page load, no error occurs because the `fetch` isn’t called until you select text, highlight it, and save an
  annotation.
- The first attempt to save triggers the invalid URL error, which is caught by the `try/catch` block and logged as
  `Error saving annotation: TypeError: URL is not valid or contains user credentials`.

**Additional Context**:

- The `index.html` is designed to send annotations to an AWS API Gateway endpoint, which forwards them to a Lambda
  function for storage in Aurora PostgreSQL (per our previous discussion).
- The placeholder URL was included as a template, expecting you to replace `<api-id>` and `<region>` with your actual
  API Gateway details after deployment.

### Fix

To resolve the error, replace the placeholder `apiUrl` with the **actual API Gateway endpoint URL** created when you
deployed your API. Below are the steps to find and apply the correct URL, along with an updated `index.html`.

#### Step 1: Find Your API Gateway URL

1. **Go to the API Gateway Console**:
    - Open the AWS Management Console (`https://console.aws.amazon.com/apigateway/`).
    - Navigate to your API (e.g., `RecogitoAPI`).
2. **Locate the Deployed Stage**:
    - Select your API and go to the **Stages** section.
    - Expand the `prod` stage (or the stage you deployed, e.g., `prod` was used in the previous setup).
    - Copy the **Invoke URL**, which looks like:
      ```
      https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
      ```
    - Append the resource path `/annotations` to form the full URL:
      ```
      https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/annotations
      ```
    - Here, `abc123xyz` is your `<api-id>`, and `us-east-1` is your `<region>`.

3. **Verify the URL**:
    - Open a browser or use `curl` to test the URL:
      ```
      curl -X POST https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/annotations -H "Content-Type: application/json" -d '{}'
      ```
    - If the Lambda is set up (per previous response), it should return a response like
      `{"message": "Annotation saved", "id": <number>}` or an error if the payload is invalid.

#### Step 2: Update `index.html`

Replace the placeholder `apiUrl` with your actual API Gateway URL. Below is the updated `index.html` with the corrected
CDN URLs (from the previous fix) and a placeholder replaced with an example API Gateway URL (substitute your own).

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

    // API Gateway endpoint (replace with your actual URL)
    const apiUrl = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/annotations';

    // Save annotation to Aurora via API Gateway
    r.on('createAnnotation', async (annotation) => {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(annotation)
            });
            const result = await response.json();
            console.log('Annotation saved:', result);
        } catch (error) {
            console.error('Error saving annotation:', error);
        }
    });

    // Optional: Load existing annotations
    async function loadAnnotations() {
        // Implement if needed
    }
</script>
</body>
</html>
```

**Important**:

- Replace `https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/annotations` with your actual API Gateway URL.
- Ensure the URL ends with `/annotations`, matching the resource path configured in API Gateway.

#### Step 3: Test the Fix

1. **Update the File**:
    - Save the updated `index.html` with your real API Gateway URL.
2. **Host the Site**:
    - **Local**: Run `python -m http.server 8000` and open `http://localhost:8000`.
    - **S3**: Upload to an S3 bucket configured for static website hosting (ensure public read access or appropriate
      permissions).
3. **Test in Browser**:
    - Open Chrome or Firefox, press F12 to open DevTools, and go to the **Console** and **Network** tabs.
    - Select text in the `<div id="content">`, create an annotation (e.g., highlight and add a comment), and save it.
    - Check the **Console** for output like `Annotation saved: { message: "Annotation saved", id: <number> }`.
    - In the **Network** tab, verify the POST request to your API Gateway URL returns a 200 status and the expected JSON
      response.
    - Query your Aurora PostgreSQL database to confirm the annotation is stored:
      ```sql
      SELECT * FROM annotations LIMIT 5;
      ```
4. **Expected Outcome**:
    - No `TypeError: URL is not valid or contains user credentials`.
    - Annotations are sent to the API Gateway and saved in the database.

#### Step 4: If You Haven’t Set Up API Gateway

If you haven’t deployed the API Gateway and Lambda function yet, the placeholder URL is the issue, and you’ll need to
complete the backend setup. Here’s a quick recap (from the previous response):

1. **Create API Gateway**:
    - In the AWS API Gateway console, create a REST API (e.g., `RecogitoAPI`).
    - Add a `/annotations` resource with a POST method.
    - Integrate with a Lambda function (e.g., `SaveRecogitoAnnotations`).
    - Enable CORS:
        - Go to **Actions** > **Enable CORS** and redeploy.
    - Deploy to the `prod` stage and copy the invoke URL.
2. **Create Lambda Function**:
    - Use the Python code provided previously, which inserts annotations into Aurora PostgreSQL via the RDS Data API.
    - Configure environment variables (`CLUSTER_ARN`, `SECRET_ARN`, `DATABASE_NAME`).
    - Assign an IAM role with `AWSLambdaBasicExecutionRole`, `AmazonRDSDataFullAccess`, and Secrets Manager access.
3. **Verify Aurora Setup**:
    - Ensure your Aurora PostgreSQL Serverless v2 cluster is running, with the `annotations` table created:
      ```sql
      CREATE TABLE annotations (
          id SERIAL PRIMARY KEY,
          annotation_id VARCHAR(255) UNIQUE NOT NULL,
          content JSONB NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
      ```

If you need help with any of these steps (e.g., deploying the API Gateway, debugging Lambda, or setting up Aurora), let
me know, and I can provide detailed guidance or additional code.

### Additional Potential Issues

If updating the URL doesn’t resolve the error, consider these edge cases:

1. **CORS Misconfiguration**:
    - If the API Gateway doesn’t return `Access-Control-Allow-Origin: *`, the `fetch` call fails with a CORS error,
      which might be misreported as a network error.
    - **Fix**: Re-enable CORS in API Gateway and redeploy. Test with `curl` to confirm the response includes CORS
      headers:
      ```
      curl -I -X POST https://your-api-id.execute-api.your-region.amazonaws.com/prod/annotations
      ```
      Look for `Access-Control-Allow-Origin: *` in the headers.

2. **Invalid API Gateway URL**:
    - If you entered a real URL but it’s incorrect (e.g., wrong `api-id`, region, or stage), `fetch` will fail.
    - **Fix**: Double-check the invoke URL in the API Gateway console. Ensure the stage (`/prod`) and resource (
      `/annotations`) match your configuration.

3. **Network Issues**:
    - If your browser or network blocks the API Gateway domain, `fetch` may fail.
    - **Fix**: Test the URL in a different browser or use `curl` from a terminal. Check the **Network** tab in DevTools
      for detailed error messages (e.g., DNS failure).

4. **Lambda or Database Errors**:
    - If the API Gateway is correct but the Lambda function fails (e.g., due to incorrect Aurora credentials or missing
      table), the `fetch` call may return a 500 error, not a `TypeError`.
    - **Fix**: Check Lambda logs in CloudWatch:
        - Go to the AWS CloudWatch console, select **Log groups**, and find `/aws/lambda/SaveRecogitoAnnotations`.
        - Look for errors (e.g., `AccessDenied` or `Table not found`).
        - Verify the Aurora cluster ARN, secret ARN, and database name in the Lambda environment variables.

5. **Browser Security**:
    - Some browsers reject URLs with unusual characters or enforce strict security policies.
    - **Fix**: Ensure the URL is clean (no trailing spaces, no credentials like `user:pass@`). Test in Chrome or
      Firefox, which have clear error reporting.

### Testing Without API Gateway (Temporary Workaround)

To confirm the `fetch` error is solely due to the invalid URL and isolate RecogitoJS functionality, temporarily replace
the `apiUrl` with a mock endpoint that accepts POST requests, such as `https://httpbin.org/post`. This won’t save to
Aurora but will verify the client-side code.

**Temporary Code**:

```javascript
const apiUrl = 'https://httpbin.org/post';
```

- Create an annotation and check the console for `Annotation saved: { ... }` with the mock response.
- If this works, the issue is confirmed to be the invalid API Gateway URL.

### Final Updated Code (with Example URL)

Here’s the `index.html` with the correct RecogitoJS CDN URLs and an example API Gateway URL (replace with yours):

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

    // API Gateway endpoint (replace with your actual URL)
    const apiUrl = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/annotations';

    // Save annotation to Aurora via API Gateway
    r.on<.on('createAnnotation', async (annotation) => {
        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(annotation)
            });
            const result = await response.json();
            console.log('Annotation saved:', result);
        } catch (error) {
            console.error('Error saving annotation:', error);
        }
    });

    // Optional: Load existing annotations
    async function loadAnnotations() {
        // Implement if needed
    }
</script>
</body>
</html>
```

**Replace** `https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/annotations` with your API Gateway URL.

### If the Error Persists

If you’ve updated the URL and still see the error, please provide:

- The **exact API Gateway URL** you’re using (redact sensitive parts if needed).
- The **full console error** (copy the stack trace from DevTools > Console).
- The **Network tab details** (status code, response headers, or error for the POST request).
- Confirmation that the API Gateway and Lambda are deployed and functional (e.g., test with `curl`).

This could indicate a subtle issue (e.g., trailing whitespace in the URL, API Gateway misconfiguration, or a
browser-specific quirk). I can debug further or provide a minimal test case.

### Final Notes

- The error is caused by the placeholder URL (`https://<api-id>.execute-api.<region>.amazonaws.com/prod/annotations`),
  which is invalid for `fetch`.
- Updating to your real API Gateway URL should resolve the `TypeError`.
- Ensure the API Gateway is deployed with CORS enabled and the Lambda function is correctly configured to handle POST
  requests.
- For production, consider hosting RecogitoJS files locally on S3 (as suggested previously) to avoid CDN issues.

Let me know if you need help finding your API Gateway URL, debugging the backend, or testing the updated code!