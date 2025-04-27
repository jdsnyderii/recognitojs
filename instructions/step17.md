Thank you for providing additional details about using **Okta OAuth tokens** with **SAML-based OAuth flows** for
authentication. This is a great clarification, as it simplifies the authentication process compared to setting up Amazon
Cognito from scratch, and it aligns well with your goal of replacing `localStorage` with Amazon S3 for annotation
storage in the `index.html` file while enabling multiple editors to collaborate on a static HTML page without
overwriting annotations.

Your request builds on our previous session (artifact ID `96200c6f-b303-426e-9559-95ac0eebd8bb`), where we implemented
RecogitoJS annotations with a sidebar, highlight toggling, multi-user filtering, an instructions overlay, and a "Clear
Annotations" button. You now want to:

- **Replace `localStorage` with S3** for storing annotations.
- **Enable multiple editors** to work on the same static HTML page (`index.html`) without overwriting annotations.
- **Use Okta with SAML-based OAuth flows** for authentication to access S3, leveraging Okta tokens to simplify the
  process.

Below, I’ll outline an approach that integrates Okta SAML-based OAuth for authentication, uses S3 for annotation
storage, and handles concurrency for multiple editors. I’ll update the `index.html` to reflect these changes, provide
setup instructions for Okta and S3, and ensure all existing features are preserved.

---

### Clarification and Assumptions

Based on your request and the context, I understand you want to:

1. **S3 for Storage**:
    - Store annotations in an S3 bucket (replacing `localStorage`).
    - Each annotation is a separate JSON file (e.g., `annotations/index.html/anno-1.json`) to minimize conflicts.
    - Load, save, update, and delete annotations via S3 operations.
2. **Multiple Editors**:
    - Multiple users edit annotations for the same `index.html` page.
    - Prevent overwrites using separate files per annotation and optimistic concurrency (e.g., check if an annotation
      exists before saving).
    - Add a “Refresh Annotations” button to sync changes from other editors (manual refresh, as S3 isn’t real-time).
3. **Okta SAML-based OAuth**:
    - Use Okta as the identity provider (IdP) with SAML-based OAuth flows to authenticate users.
    - Obtain Okta OAuth tokens to authenticate S3 requests, likely via AWS Security Token Service (STS) to assume an IAM
      role with S3 permissions.
    - Avoid hardcoding AWS credentials; use Okta tokens to securely access S3.
4. **Static Site**:
    - Keep `index.html` as a single static file, hosted on S3 or locally.
    - Use client-side JavaScript (AWS SDK) for S3 operations.
    - No backend server (e.g., Node.js), maintaining static site compatibility.
5. **Preserve Features**:
    - Retain sidebar toggle, highlight toggling (one annotation highlighted when sidebar open), multi-user filter,
      instructions overlay, and “Clear Annotations.”
    - Update “Clear Annotations” to delete all annotation files in S3 for the page.
6. **Concurrency**:
    - Handle low concurrency (2–5 editors) with separate files and conditional writes.
    - No real-time updates; rely on manual refresh for simplicity.

**Assumptions** (please confirm or clarify):

- **S3 Bucket**: One bucket (e.g., `my-annotations-bucket`) with a folder per page (e.g., `annotations/index.html/`).
  Annotations are stored as `anno-<id>.json`.
- **Okta Setup**: You have an Okta tenant with a SAML application configured, and you can provide the SAML metadata (or
  SAML assertion endpoint) and OAuth client details (client ID, redirect URI).
- **AWS Integration**: Okta SAML will be used to assume an AWS IAM role via AWS STS, granting S3 permissions (
  `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`).
- **Page ID**: Annotations are tied to the page’s URL (`index.html`) or a unique ID (e.g., `page1`).
- **Refresh Mechanism**: A “Refresh Annotations” button is sufficient to sync changes (no polling or WebSocket for
  real-time updates).
- **Clear Annotations**: Deletes all annotations for the page in S3, accessible to all authenticated users.

**Questions** (optional, to refine the solution):

1. **Okta Details**: Do you have the Okta SAML application’s metadata URL, client ID, or redirect URI? Should the app
   use OAuth 2.0 with SAML assertion grants or pure SAML to AWS?
2. **S3 Path**: Should the S3 folder be based on the page’s URL (`index.html`), a custom ID, or something else?
3. **Concurrency Needs**: How many editors are expected? Is manual refresh okay, or do you want periodic auto-refresh (
   e.g., every 30 seconds)?
4. **Clear Annotations Scope**: Should it delete all annotations in S3 for the page, or only the current user’s?
5. **Error Handling**: How should conflicts (e.g., two editors saving the same annotation) be handled? (E.g., prompt
   user, overwrite, or skip.)

For now, I’ll assume:

- **Okta SAML to AWS**: Use Okta’s SAML integration to assume an AWS IAM role via STS, obtaining temporary credentials
  for S3 access.
- **S3 Structure**: Bucket `my-annotations-bucket`, folder `annotations/index.html/`, files `anno-<id>.json`.
- **Manual Refresh**: Add a “Refresh Annotations” button.
- **Clear Annotations**: Deletes all annotations in the page’s S3 folder.
- **Low Concurrency**: 2–5 editors, with separate files and conditional writes to avoid conflicts.

If these assumptions don’t align, please provide details, and I’ll adjust.

---

### Challenges and Considerations

1. **Okta SAML-based OAuth**:
    - Okta’s SAML integration with AWS typically uses SAML assertions to assume an IAM role via AWS STS, generating
      temporary credentials (access key, secret key, session token).
    - OAuth tokens alone don’t directly authenticate S3 requests; we’ll use Okta’s SAML flow to get AWS credentials, as
      S3 requires AWS IAM authentication.
    - The static site needs a client-side SAML flow, which involves redirecting to Okta’s login page and handling the
      SAML response to exchange for AWS credentials.
    - Okta’s OAuth 2.0 with SAML assertion grant is less common for AWS; SAML-to-STS is standard and simpler for S3
      access.
2. **S3 Storage**:
    - Replacing `localStorage` requires asynchronous AWS SDK calls (`ListObjectsV2`, `GetObject`, `PutObject`,
      `DeleteObject`).
    - Separate files per annotation reduce conflicts but require listing and fetching multiple objects.
    - S3’s eventual consistency may delay updates; we’ll use `HeadObject` to check for conflicts.
3. **Concurrency**:
    - Separate files minimize conflicts, as RecogitoJS generates unique annotation IDs.
    - Conditional writes (e.g., `If-None-Match`) prevent overwrites for new annotations.
    - For updates, check the annotation’s timestamp or version to reject stale saves.
    - Manual refresh is simple but requires user action; auto-refresh adds complexity.
4. **Static Site**:
    - The AWS SDK and Okta’s JavaScript library (e.g., Okta Auth JS) run client-side.
    - SAML redirects to Okta’s login page, which may disrupt the UX; we’ll store state to resume seamlessly.
    - CORS and bucket policies must allow client-side S3 access.
5. **Security**:
    - Okta SAML ensures secure authentication without exposing AWS credentials.
    - IAM roles restrict S3 access to authenticated users.
    - Annotations are public within the bucket unless restricted by user-specific paths or policies.

---

### Proposed Approach

Here’s how we’ll implement S3 storage with Okta SAML-based authentication for multiple editors:

1. **S3 Bucket Structure**:
    - Bucket: `my-annotations-bucket`.
    - Folder: `annotations/index.html/` (based on page URL, sanitized for S3).
    - Files: `anno-<id>.json` (e.g., `anno-1.json`), each containing one annotation object.
    - Example:
      ```
      my-annotations-bucket/
        annotations/
          index.html/
            anno-1.json
            anno-2.json
      ```

2. **Okta SAML Authentication**:
    - Use Okta’s SAML application to authenticate users and assume an AWS IAM role via AWS STS.
    - Flow:
        - User loads `index.html`; if unauthenticated, redirect to Okta’s SAML login page.
        - After login, Okta redirects back with a SAML assertion.
        - Client-side JavaScript exchanges the SAML assertion with AWS STS (`AssumeRoleWithSAML`) to get temporary
          credentials.
        - Use credentials to initialize the AWS SDK for S3 operations.
    - Use Okta Auth JS for the login flow and AWS SDK for STS and S3.
    - Store credentials in memory (not `localStorage`) for security.

3. **AWS SDK Integration**:
    - Include AWS SDK via CDN (`aws-sdk`).
    - Configure S3 client with temporary credentials from STS.
    - Replace `localStorage` operations:
        - **Load**: `ListObjectsV2` to get all `anno-*.json` files, `GetObject` to fetch each.
        - **Save**: `PutObject` to write `anno-<id>.json`, with `If-None-Match` for new annotations.
        - **Delete**: `DeleteObject` to remove `anno-<id>.json`.
        - **Clear**: `DeleteObjects` to remove all files in `annotations/index.html/`.
    - Add a “Refresh Annotations” button to re-fetch annotations.

4. **Concurrency Management**:
    - **Separate Files**: Each annotation is a unique file, reducing conflicts.
    - **Conditional Writes**:
        - For new annotations, use `If-None-Match: *` to fail if the file exists.
        - For updates, include a `version` field (timestamp) in annotations; check the existing file’s version before
          saving.
    - **Conflict Resolution**: If a conflict is detected (e.g., newer version exists), alert the user to refresh and
      retry.
    - **Refresh Button**: Triggers a full reload of annotations to sync with other editors’ changes.

5. **Update `index.html`**:
    - Add AWS SDK and Okta Auth JS scripts.
    - Implement a login UI (e.g., “Sign in with Okta” button) that redirects to Okta’s SAML endpoint.
    - Replace `localStorage` with S3 operations using async functions.
    - Add a “Refresh Annotations” button to `#controls`.
    - Preserve all features: sidebar toggle, highlight toggling, multi-user filter, instructions overlay, and “Clear
      Annotations.”
    - Handle errors (e.g., expired tokens, S3 failures) with user-friendly alerts.

6. **S3 and AWS Configuration**:
    - **Bucket Policy**:
      ```json
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
              "AWS": "arn:aws:iam::<account-id>:role/OktaSAMLRole"
            },
            "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
            "Resource": [
              "arn:aws:s3:::my-annotations-bucket/*",
              "arn:aws:s3:::my-annotations-bucket"
            ]
          }
        ]
      }
      ```
    - **CORS Configuration**:
      ```json
      [
        {
          "AllowedHeaders": ["*"],
          "AllowedMethods": ["GET", "PUT", "DELETE", "HEAD"],
          "AllowedOrigins": ["https://<bucket-name>.s3-website-<region>.amazonaws.com"],
          "ExposeHeaders": [],
          "MaxAgeSeconds": 3000
        }
      ]
      ```
    - **IAM Role** (`OktaSAMLRole`):
        - Trust relationship with Okta’s SAML provider.
        - Permissions for S3 actions.
    - Enable static website hosting for the bucket.

7. **Okta Configuration**:
    - Create a SAML application in Okta:
        - Single Sign-On URL: AWS STS endpoint (e.g., `https://signin.aws.amazon.com/saml`).
        - Audience URI: `urn:amazon:webservices`.
        - Attribute statements to map Okta user attributes to AWS roles.
    - Obtain client-side details: Okta domain (e.g., `https://your-org.okta.com`), client ID, and redirect URI.
    - Use Okta Auth JS to initiate the SAML flow.

---

### Updated `index.html`

I’ll update the previous `index.html` to:

- Replace `localStorage` with S3 operations using the AWS SDK.
- Add Okta SAML-based authentication via Okta Auth JS and AWS STS.
- Add a “Refresh Annotations” button to sync changes.
- Handle concurrency with separate files and conditional writes.
- Preserve all features (sidebar, highlight toggling, filter, instructions, clear).
- Use the same `artifact_id` (`96200c6f-b303-426e-9559-95ac0eebd8bb`).

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecogitoJS Annotations with S3</title>
    <link href="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@recogito/recogito-js@1.8.2/dist/recogito.min.js"></script>
    <script src="https://unpkg.com/aws-sdk@2.1418.0/dist/aws-sdk.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@okta/okta-auth-js@7.8.0/dist/okta-auth-js.min.js"></script>
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
        #auth-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 5;
        }
        #auth-container.hidden {
            display: none;
        }
        #auth-container button {
            padding: 10px 20px;
            background: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1em;
        }
        #auth-container button:hover {
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
<div id="auth-container">
    <button id="sign-in-button">Sign in with Okta</button>
</div>
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
    // Okta and AWS configuration (replace with your values)
    const OKTA_DOMAIN = 'https://your-org.okta.com';
    const OKTA_CLIENT_ID = 'your-okta-client-id';
    const REDIRECT_URI = 'https://<bucket-name>.s3-website-<region>.amazonaws.com/index.html';
    const AWS_REGION = 'us-east-1';
    const S3_BUCKET = 'my-annotations-bucket';
    const S3_PREFIX = 'annotations/index.html/';
    const ROLE_ARN = 'arn:aws:iam::<account-id>:role/OktaSAMLRole';
    const SAML_PROVIDER_ARN = 'arn:aws:iam::<account-id>:saml-provider/Okta';

    // Initialize Okta Auth JS
    const oktaAuth = new OktaAuth({
        issuer: `${OKTA_DOMAIN}/oauth2/default`,
        clientId: OKTA_CLIENT_ID,
        redirectUri: REDIRECT_URI,
        scopes: ['openid', 'profile', 'email']
    });

    // Initialize RecogitoJS
    const r = Recogito.init({
        content: document.getElementById('content'),
        mode: 'ANNOTATION',
        formatter: (annotation) => {
            return { className: 'r6o-annotation' };
        }
    });

    // State variables
    let currentUser = '';
    let selectedAnnotationId = null;
    let isSidebarVisible = true; // Default to visible
    let s3Client = null;
    const userInput = document.getElementById('user-input');
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle');
    const content = document.getElementById('content');
    const instructionsButton = document.getElementById('instructions-button');
    const instructionsOverlay = document.getElementById('instructions-overlay');
    const authContainer = document.getElementById('auth-container');
    const signInButton = document.getElementById('sign-in-button');

    // Authentication flow
    async function authenticate() {
        try {
            // Check if redirected back from Okta
            if (oktaAuth.isLoginRedirect()) {
                const tokens = await oktaAuth.handleLoginRedirect();
                const idToken = tokens.idToken.idToken;
                // Exchange ID token for AWS credentials via SAML
                const sts = new AWS.STS({ region: AWS_REGION });
                const samlResponse = await fetchSAMLAssertion(idToken); // Custom function, see setup
                const params = {
                    PrincipalArn: SAML_PROVIDER_ARN,
                    RoleArn: ROLE_ARN,
                    SAMLAssertion: samlResponse
                };
                const credentials = await sts.assumeRoleWithSAML(params).promise();
                AWS.config.credentials = new AWS.Credentials({
                    accessKeyId: credentials.Credentials.AccessKeyId,
                    secretAccessKey: credentials.Credentials.SecretAccessKey,
                    sessionToken: credentials.Credentials.SessionToken
                });
                s3Client = new AWS.S3({ region: AWS_REGION });
                authContainer.classList.add('hidden');
                currentUser = tokens.idToken.claims.email.split('@')[0];
                userInput.value = currentUser;
                loadAnnotations();
            } else if (await oktaAuth.isAuthenticated()) {
                // Already authenticated
                const tokens = await oktaAuth.token.getWithoutPrompt();
                const idToken = tokens.idToken.idToken;
                const sts = new AWS.STS({ region: AWS_REGION });
                const samlResponse = await fetchSAMLAssertion(idToken);
                const params = {
                    PrincipalArn: SAML_PROVIDER_ARN,
                    RoleArn: ROLE_ARN,
                    SAMLAssertion: samlResponse
                };
                const credentials = await sts.assumeRoleWithSAML(params).promise();
                AWS.config.credentials = new AWS.Credentials({
                    accessKeyId: credentials.Credentials.AccessKeyId,
                    secretAccessKey: credentials.Credentials.SecretAccessKey,
                    sessionToken: credentials.Credentials.SessionToken
                });
                s3Client = new AWS.S3({ region: AWS_REGION });
                authContainer.classList.add('hidden');
                currentUser = tokens.idToken.claims.email.split('@')[0];
                userInput.value = currentUser;
                loadAnnotations();
            } else {
                // Show sign-in button
                authContainer.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Authentication error:', error);
            alert('Failed to authenticate. Please try again.');
        }
    }

    // Placeholder for fetching SAML assertion (customize based on Okta setup)
    async function fetchSAMLAssertion(idToken) {
        // This requires a backend or Okta API call to exchange ID token for SAML assertion
        // For simplicity, assume a custom endpoint or manual configuration
        console.warn('fetchSAMLAssertion not implemented. Replace with Okta API call or backend.');
        return 'mock-saml-assertion'; // Replace with actual SAML assertion
    }

    // Sign-in button handler
    signInButton.addEventListener('click', () => {
        oktaAuth.signInWithRedirect();
    });

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

    // Toggle sidebar visibility and highlights
    function toggleSidebar() {
        isSidebarVisible = !isSidebarVisible;
        selectedAnnotationId = null;
        instructionsOverlay.classList.add('hidden');
        localStorage.setItem('sidebarVisible', isSidebarVisible);
        updateSidebarVisibility();
    }

    // Handle toggle button click
    toggleButton.addEventListener('click', toggleSidebar);

    // Handle instructions button click
    instructionsButton.addEventListener('click', () => {
        instructionsOverlay.classList.remove('hidden');
    });

    // Load annotations from S3
    async function loadAnnotations() {
        if (!s3Client) return;
        try {
            const listParams = {
                Bucket: S3_BUCKET,
                Prefix: S3_PREFIX
            };
            const data = await s3Client.listObjectsV2(listParams).promise();
            const annotations = [];
            for (const obj of data.Contents) {
                const getParams = {
                    Bucket: S3_BUCKET,
                    Key: obj.Key
                };
                const file = await s3Client.getObject(getParams).promise();
                const annotation = JSON.parse(file.Body.toString());
                annotations.push(annotation);
            }
            r.setAnnotations(annotations);
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Loaded annotations:', annotations);
        } catch (error) {
            console.error('Error loading annotations:', error);
            alert('Failed to load annotations from S3.');
        }
    }

    // Save annotation to S3
    async function saveAnnotation(annotation) {
        if (!s3Client) return;
        try {
            const updatedAnnotation = {
                ...annotation,
                creator: {
                    type: 'Person',
                    name: currentUser || 'Anonymous'
                },
                version: new Date().toISOString() // For concurrency
            };
            const key = `${S3_PREFIX}${annotation.id}.json`;
            // Check for conflicts
            try {
                const headParams = {
                    Bucket: S3_BUCKET,
                    Key: key
                };
                const existing = await s3Client.headObject(headParams).promise();
                const getParams = {
                    Bucket: S3_BUCKET,
                    Key: key
                };
                const file = await s3Client.getObject(getParams).promise();
                const existingAnnotation = JSON.parse(file.Body.toString());
                if (existingAnnotation.version > updatedAnnotation.version) {
                    alert('Annotation was updated by another user. Please refresh.');
                    return;
                }
            } catch (error) {
                if (error.code !== 'NotFound') throw error;
            }
            const putParams = {
                Bucket: S3_BUCKET,
                Key: key,
                Body: JSON.stringify(updatedAnnotation),
                ContentType: 'application/json',
                IfNoneMatch: '*' // Prevent overwrite for new annotations
            };
            await s3Client.putObject(putParams).promise();
            const annotations = await fetchAnnotations();
            updateSidebar(annotations);
            updateUserFilter(annotations);
            console.log('Annotation saved:', updatedAnnotation);
        } catch (error) {
            console.error('Error saving annotation:', error);
            alert('Failed to save annotation to S3.');
        }
    }

    // Fetch all annotations (helper)
    async function fetchAnnotations() {
        const listParams = {
            Bucket: S3_BUCKET,
            Prefix: S3_PREFIX
        };
        const data = await s3Client.listObjectsV2(listParams).promise();
        const annotations = [];
        for (const obj of data.Contents) {
            const getParams = {
                Bucket: S3_BUCKET,
                Key: obj.Key
            };
            const file = await s3Client.getObject(getParams).promise();
            const annotation = JSON.parse(file.Body.toString());
            annotations.push(annotation);
        }
        return annotations;
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

    // Clear annotations from S3
    async function clearAnnotations() {
        if (!s3Client) return;
        try {
            const listParams = {
                Bucket: S3_BUCKET,
                Prefix: S3_PREFIX
            };
            const data = await s3Client.listObjectsV2(listParams).promise();
            if (data.Contents.length > 0) {
                const deleteParams = {
                    Bucket: S3_BUCKET,
                    Delete: {
                        Objects: data.Contents.map(obj => ({ Key: obj.Key }))
                    }
                };
                await s3Client.deleteObjects(deleteParams).promise();
            }
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
            alert('Failed to clear annotations from S3.');
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
        if (!s3Client) return;
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const annotations = JSON.parse(e.target.result);
                    for (const annotation of annotations) {
                        const key = `${S3_PREFIX}${annotation.id}.json`;
                        const putParams = {
                            Bucket: S3_BUCKET,
                            Key: key,
                            Body: JSON.stringify(annotation),
                            ContentType: 'application/json'
                        };
                        await s3Client.putObject(putParams).promise();
                    }
                    r.setAnnotations(annotations);
                    selectedAnnotationId = null;
                    updateSidebar(annotations);
                    updateUserFilter(annotations);
                    console.log('Imported annotations:', annotations);
                } catch (error) {
                    console.error('Error importing annotations:', error);
                    alert('Failed to import annotations to S3.');
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
        if (!s3Client) return;
        try {
            const key = `${S3_PREFIX}${annotation.id}.json`;
            await s3Client.deleteObject({ Bucket: S3_BUCKET, Key: key }).promise();
            const annotations = await fetchAnnotations();
            updateSidebar(annotations);
            updateUserFilter(annotations);
            if (selectedAnnotationId === annotation.id) {
                selectedAnnotationId = null;
            }
            console.log('Annotation deleted:', annotation);
        } catch (error) {
            console.error('Error deleting annotation:', error);
            alert('Failed to delete annotation from S3.');
        }
    });

    // Initialize authentication
    authenticate();
</script>
</body>
</html>
```

---

### Setup Instructions

1. **Okta Configuration**:
    - **Create SAML Application**:
        - In Okta Admin Console, create a SAML 2.0 application.
        - Set Single Sign-On URL: `https://signin.aws.amazon.com/saml`.
        - Set Audience URI: `urn:amazon:webservices`.
        - Add attribute statements:
            - `https://aws.amazon.com/SAML/Attributes/Role`:
              `arn:aws:iam::<account-id>:role/OktaSAMLRole,arn:aws:iam::<account-id>:saml-provider/Okta`.
            - `https://aws.amazon.com/SAML/Attributes/RoleSessionName`: User email or ID.
        - Note the SAML metadata URL (e.g., `https://your-org.okta.com/app/<app-id>/sso/saml/metadata`).
    - **Create OAuth Application** (optional, for Okta Auth JS):
        - Create an OIDC application for client-side auth.
        - Set Client ID, Redirect URI (e.g., `https://<bucket-name>.s3-website-<region>.amazonaws.com/index.html`).
        - Enable “SAML 2.0” as a token exchange grant type if needed.
    - Update `index.html` with:
        - `OKTA_DOMAIN`: Your Okta domain (e.g., `https://your-org.okta.com`).
        - `OKTA_CLIENT_ID`: OIDC client ID.
        - `REDIRECT_URI`: Page URL.

2. **AWS Configuration**:
    - **Create S3 Bucket**:
        - Name: `my-annotations-bucket`.
        - Enable static website hosting (set `index.html` as index document).
        - Apply bucket policy (see above).
        - Set CORS configuration (see above).
    - **Create SAML Provider**:
        - In IAM, create a SAML provider named “Okta”.
        - Upload Okta’s SAML metadata (from metadata URL).
        - Note the ARN: `arn:aws:iam::<account-id>:saml-provider/Okta`.
    - **Create IAM Role** (`OktaSAMLRole`):
        - Trust relationship:
          ```json
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Principal": {
                  "Federated": "arn:aws:iam::<account-id>:saml-provider/Okta"
                },
                "Action": "sts:AssumeRoleWithSAML",
                "Condition": {
                  "StringEquals": {
                    "SAML:aud": "https://signin.aws.amazon.com/saml"
                  }
                }
              }
            ]
          }
          ```
        - Policy:
          ```json
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
                "Resource": [
                  "arn:aws:s3:::my-annotations-bucket/*",
                  "arn:aws:s3:::my-annotations-bucket"
                ]
              }
            ]
          }
          ```
        - Note the ARN: `arn:aws:iam::<account-id>:role/OktaSAMLRole`.
    - Update `index.html` with:
        - `AWS_REGION`: Your region (e.g., `us-east-1`).
        - `S3_BUCKET`: `my-annotations-bucket`.
        - `ROLE_ARN`: IAM role ARN.
        - `SAML_PROVIDER_ARN`: SAML provider ARN.

3. **Deploy the Site**:
    - Upload `index.html` to the S3 bucket (`my-annotations-bucket`).
    - Set public read access for `index.html`:
      ```bash
      aws s3api put-object-acl --bucket my-annotations-bucket --key index.html --acl public-read
      ```
    - Access the site: `https://<bucket-name>.s3-website-<region>.amazonaws.com/index.html`.

4. **Test Authentication**:
    - Open the site; see “Sign in with Okta” button.
    - Click to redirect to Okta’s login page.
    - Sign in; redirect back to the site.
    - Verify `#auth-container` hides, and annotations load.

5. **Test Annotations**:
    - Create an annotation; check S3 for `annotations/index.html/anno-<id>.json`.
    - Toggle highlights, filter, clear, and refresh; ensure S3 updates correctly.
    - Test with multiple browsers/users to simulate concurrent edits.

---

### Limitations and Notes

- **SAML Assertion**: The `fetchSAMLAssertion` function is a placeholder. You’ll need a backend or Okta API to exchange
  the ID token for a SAML assertion. Alternatively, use Okta’s SAML redirect flow directly with AWS SDK’s
  `AssumeRoleWithSAML` (requires parsing the SAML response from the redirect).
- **Concurrency**: Separate files and version checks handle most conflicts, but rare cases (e.g., two editors updating
  the same annotation) may require user intervention (refresh and retry).
- **Refresh**: Manual refresh is simple; auto-refresh (e.g., every 30 seconds) can be added if needed.
- **Performance**: Fetching many annotations may be slow; consider caching locally (in memory) and fetching deltas.
- **Security**: Annotations are accessible to all authenticated users; add user-specific paths (e.g.,
  `annotations/<user>/`) if needed.

---

### Testing Instructions

1. **Deploy**:
    - Upload `index.html` to S3 with public read access.
    - Configure Okta and AWS as above.
2. **Test Authentication**:
    - Open the site; click “Sign in with Okta”.
    - Log in via Okta; verify redirect back and `#auth-container` hides.
    - Check `currentUser` is set from Okta email.
3. **Test Annotations**:
    - Create an annotation; verify `anno-<id>.json` in S3.
    - Update/delete; confirm S3 updates.
    - Click “Refresh Annotations”; ensure new annotations from other users load.
    - Click “Clear Annotations”; verify all files in `annotations/index.html/` are deleted.
4. **Test Concurrency**:
    - Open two browsers as different users.
    - Create annotations simultaneously; confirm separate files (`anno-1.json`, `anno-2.json`).
    - Update the same annotation; verify conflict alert (requires refresh).
5. **Test Features**:
    - Toggle sidebar/highlights, filter users, open instructions, export/import.
    - Ensure all work with S3 backend.
6. **Responsive Design**:
    - Test on mobile (<768px); verify login, overlay, and buttons.

---

### Troubleshooting

- **Authentication Fails**:
    - Check Okta domain, client ID, and redirect URI.
    - Verify SAML provider and IAM role ARNs.
    - Inspect Console for errors; ensure `fetchSAMLAssertion` returns a valid assertion.
- **S3 Errors**:
    - Confirm bucket policy and CORS.
    - Check IAM role permissions.
    - Verify `S3_BUCKET` and `S3_PREFIX`.
- **Concurrency Conflicts**:
    - Test with multiple users; ensure `version` checks prevent overwrites.
    - Add `console.log` in `saveAnnotation` to debug.
- **Annotations Not Loading**:
    - Check S3 file structure (`annotations/index.html/`).
    - Verify `ListObjectsV2` returns files (add `console.log(data.Contents)`).
- **Provide Details**:
    - Share errors, browser, Okta/AWS config, or S3 contents.

---

### Enhancements (Optional)

- **Auto-Refresh**:
    - Add periodic refresh:
      ```javascript
      setInterval(refreshAnnotations, 30000);
      ```
- **User-Specific Annotations**:
    - Store annotations in `annotations/<user>/index.html/` to restrict access.
- **Conflict UI**:
    - Show a modal with merge options for conflicts.
- **Local Caching**:
    - Cache annotations in memory to reduce S3 calls.

---

### Final Notes

- The updated `index.html` replaces `localStorage` with S3, uses Okta SAML-based OAuth for authentication, and supports
  multiple editors with concurrency handling.
- All features (highlight toggling, sidebar, filter, instructions, clear) are preserved.
- The solution is client-side, suitable for S3 static hosting.
- **SAML Assertion**: You’ll need to implement `fetchSAMLAssertion` or use a backend to exchange Okta tokens for SAML
  assertions. Let me know if you need help with this.

Please test the updated file and let me know if it meets your needs or if you need adjustments (e.g., Okta setup help,
different S3 structure, or enhanced concurrency). If you have more ideas, I’m ready to keep going!