To store annotations from **RecogitoJS** in a serverless **Amazon Aurora PostgreSQL** or **Aurora MySQL** database on
AWS, you need to integrate RecogitoJS’s client-side annotation functionality with AWS services, leveraging the **RDS
Data API** for serverless database interactions. RecogitoJS generates annotations in the W3C Web Annotation Data Model (
JSON format), which can be saved to a database using AWS Lambda for serverless compute and AWS Secrets Manager for
secure credential management. Below, I explain the process step-by-step, including setup, code, and considerations for
both Aurora PostgreSQL and Aurora MySQL, tailored for a static HTML site.

---

### Overview of the Solution

1. **RecogitoJS Setup**: Capture annotations client-side and send them to an AWS endpoint.
2. **AWS Architecture**:
    - **Amazon API Gateway**: Exposes an HTTP endpoint to receive annotation data from the client.
    - **AWS Lambda**: Processes the annotation data and interacts with the Aurora database via the RDS Data API.
    - **Amazon Aurora Serverless v2 (PostgreSQL or MySQL)**: Stores the annotations in a serverless database.
    - **AWS Secrets Manager**: Securely stores database credentials.
    - **IAM Roles**: Ensures secure access between services.
3. **Static Site Integration**: Use JavaScript (e.g., `fetch`) to send annotations from the static HTML site to the API
   Gateway.
4. **Database Schema**: Store annotations in a table designed for the W3C Web Annotation format.

This approach is serverless, cost-effective, and scalable, aligning with Aurora Serverless v2’s auto-scaling
capabilities.[](https://aws.amazon.com/rds/aurora/serverless/)

---

### Step-by-Step Implementation

#### 1. **Set Up Amazon Aurora Serverless v2**

- **Choose Database Engine**:
    - **Aurora PostgreSQL**: Preferred for its robust support for JSON data types (`jsonb`) and RDS Data API
      compatibility with Serverless
      v2.[](https://dev.to/aws-builders/amazon-aurora-postgresql-now-supports-rds-data-api-51a1)
    - **Aurora MySQL**: Viable but less ideal due to limited JSON support and no RDS Data API support for Serverless v2
      in some configurations.[](https://dev.to/aws-builders/amazon-aurora-postgresql-now-supports-rds-data-api-51a1)
    - **Recommendation**: Use Aurora PostgreSQL for better JSON handling and Data API support.
- **Create Aurora Serverless v2 Cluster**:
    1. Sign in to the AWS Management Console and navigate to the **Amazon RDS console** (
       `https://console.aws.amazon.com/rds/`).
    2. Click **Create database**, select **Standard create**, and choose **Amazon Aurora**.
    3. Select **PostgreSQL-compatible** (or MySQL-compatible) and **Serverless v2**.
    4. Configure:
        - **DB cluster identifier**: e.g., `recogito-annotations`.
        - **Master username**: e.g., `admin`.
        - **Master password**: Store in AWS Secrets Manager (auto-generated).
        - **Capacity range**: Set min/max Aurora Capacity Units (e.g., 0.5–8 ACUs for cost efficiency).
        - **VPC and Security Group**: Place in a private subnet with a security group allowing Lambda access (port 5432
          for PostgreSQL, 3306 for MySQL).
        - **Enable RDS Data API**: Check the box under **Additional configuration** (required for serverless
          queries).[](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html)
    5. Create the cluster and note the **Cluster ARN** and **Secret ARN** from Secrets Manager.
- **Cost Note**: Aurora Serverless v2 costs ~$0.06–$0.12 per ACU-hour, with minimal usage (<$1) if you delete resources
  after
  testing.[](https://aws.amazon.com/pt/getting-started/hands-on/configure-connect-serverless-mysql-database-aurora/)

#### 2. **Design the Database Schema**

- **Table Structure**:
    - Create a table to store annotations, accommodating the W3C Web Annotation format (JSON or structured fields).
    - For **PostgreSQL**, use `jsonb` for flexible storage of the full annotation object.
    - For **MySQL**, use `JSON` or structured columns (less flexible due to weaker JSON support).

- **PostgreSQL Schema**:
  ```sql
  CREATE TABLE annotations (
      id SERIAL PRIMARY KEY,
      annotation_id VARCHAR(255) UNIQUE NOT NULL,
      content JSONB NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

- **MySQL Schema** (simplified, as JSON support is less robust):
  ```sql
  CREATE TABLE annotations (
      id INT AUTO_INCREMENT PRIMARY KEY,
      annotation_id VARCHAR(255) UNIQUE NOT NULL,
      content JSON NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

- **Explanation**:
    - `annotation_id`: Stores the unique `@id` from the W3C annotation (e.g., a UUID or URI).
    - `content`: Stores the full JSON annotation (e.g.,
      `{ "@context": "...", "id": "...", "body": [...], "target": "..." }`).
    - `created_at`/`updated_at`: Tracks annotation timestamps.
    - PostgreSQL’s `jsonb` allows efficient querying of JSON fields (e.g., `content->>'creator'`), while MySQL’s `JSON`
      is less queryable.

- **Create the Table**:
    - Use the RDS Query Editor or a temporary AWS Cloud9 instance to run the SQL. Ensure the security group allows
      access from
      Cloud9.[](https://aws.amazon.com/pt/getting-started/hands-on/configure-connect-serverless-mysql-database-aurora/)

#### 3. **Set Up AWS Lambda and API Gateway**

- **Create an IAM Role for Lambda**:
    1. In the **IAM console**, create a role (e.g., `LambdaAuroraRole`).
    2. Attach policies:
        - `AWSLambdaBasicExecutionRole` (for CloudWatch logs).
        - `AmazonRDSDataFullAccess` (for RDS Data API).
        - Custom policy for Secrets Manager:
          ```json
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": "secretsmanager:GetSecretValue",
                "Resource": "<your-secret-arn>"
              }
            ]
          }
          ```
    3. Note the role ARN.

- **Create a Lambda Function**:
    1. In the **Lambda console**, create a function (e.g., `SaveRecogitoAnnotations`).
    2. Choose **Python 3.9** (or later) as the runtime.
    3. Assign the `LambdaAuroraRole`.
    4. Add environment variables:
        - `CLUSTER_ARN`: Your Aurora cluster ARN.
        - `SECRET_ARN`: Your Secrets Manager secret ARN.
        - `DATABASE_NAME`: e.g., `postgres` (default for PostgreSQL) or `annotations_db` (MySQL).

- **Lambda Code** (Python for PostgreSQL):
  ```python
  import json
  import boto3
  import os

  rds_data = boto3.client('rds-data')

  def lambda_handler(event, context):
      try:
          # Parse annotation from API Gateway
          body = json.loads(event['body'])
          annotation_id = body.get('id')
          content = body  # Full W3C annotation JSON

          # Database parameters
          cluster_arn = os.environ['CLUSTER_ARN']
          secret_arn = os.environ['SECRET_ARN']
          database_name = os.environ['DATABASE_NAME']

          # Insert annotation
          sql = """
              INSERT INTO annotations (annotation_id, content)
              VALUES (:annotation_id, :content)
              ON CONFLICT (annotation_id) DO UPDATE
              SET content = EXCLUDED.content, updated_at = CURRENT_TIMESTAMP
              RETURNING id
          """
          parameters = [
              {'name': 'annotation_id', 'value': {'stringValue': annotation_id}},
              {'name': 'content', 'value': {'stringValue': json.dumps(content)}}
          ]

          response = rds_data.execute_statement(
              resourceArn=cluster_arn,
              secretArn=secret_arn,
              database=database_name,
              sql=sql,
              parameters=parameters
          )

          return {
              'statusCode': 200,
              'body': json.dumps({'message': 'Annotation saved', 'id': response['records'][0][0]['longValue']})
          }
      except Exception as e:
          return {
              'statusCode': 500,
              'body': json.dumps({'error': str(e)})
          }
  ```

- **MySQL Lambda Adjustment**:
    - Replace the SQL with:
      ```sql
      INSERT INTO annotations (annotation_id, content)
      VALUES (:annotation_id, :content)
      ON DUPLICATE KEY UPDATE
      content = VALUES(content), updated_at = CURRENT_TIMESTAMP;
      ```
    - MySQL uses `ON DUPLICATE KEY UPDATE` instead of PostgreSQL’s `ON CONFLICT`.

- **Deploy the Function**:
    - Save and deploy the Lambda function.

- **Create API Gateway**:
    1. In the **API Gateway console**, create a **REST API** (e.g., `RecogitoAPI`).
    2. Create a **POST** method under a resource (e.g., `/annotations`).
    3. Integrate with the Lambda function (`SaveRecogitoAnnotations`).
    4. Enable **CORS** for static site access.
    5. Deploy the API to a stage (e.g., `prod`) and note the invoke URL (e.g.,
       `https://<api-id>.execute-api.<region>.amazonaws.com/prod/annotations`).

#### 4. **Integrate RecogitoJS in Static HTML**

- **RecogitoJS Setup**:
    - Include RecogitoJS in your static HTML site (via CDN or local files).
    - Capture annotations and send them to the API Gateway.

- **HTML and JavaScript**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecogitoJS Annotations</title>
    <link href="https://cdn.jsdelivr.net/npm/recogito@1.8.2/dist/recogito.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/recogito@1.8.2/dist/recogito.min.js"></script>
</head>
<body>
<div id="content">Text to annotate.</div>
<script>
    // Initialize RecogitoJS
    const r = Recogito.init({
        content: document.getElementById('content'),
        mode: 'pre'
    });

    // API Gateway endpoint
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

    // Optional: Load existing annotations
    async function loadAnnotations() {
        // Implement if needed (e.g., fetch from another API endpoint)
    }
</script>
</body>
</html>
```

- **Explanation**:
    - RecogitoJS is initialized on a `<div>` with annotatable content.
    - The `createAnnotation` event triggers a `fetch` request to the API Gateway, sending the W3C annotation JSON.
    - Replace `<api-id>` and `<region>` with your API Gateway invoke URL.
    - CORS must be enabled in API Gateway to allow requests from the static site.

#### 5. **Security and Networking**

- **VPC Configuration**:
    - Place the Aurora cluster in a private subnet within a VPC.
    - Configure the Lambda function to run in the same VPC (add VPC settings in the Lambda console).
    - Update the Aurora security group to allow inbound traffic from the Lambda security group on port 5432 (PostgreSQL)
      or 3306 (
      MySQL).[](https://aws.amazon.com/pt/getting-started/hands-on/configure-connect-serverless-mysql-database-aurora/)
- **IAM Authentication** (Optional):
    - Enable IAM database authentication in Aurora and grant the Lambda role `rds_iam` privileges for secure,
      passwordless
      access.[](https://aws.amazon.com/blogs/database/iam-role-based-authentication-to-amazon-aurora-from-serverless-applications/)
- **Secrets Manager**:
    - Ensure the Secret ARN contains the database credentials, accessible by the Lambda role.

#### 6. **Testing and Deployment**

- **Test the Static Site**:
    - Host the HTML file on an S3 bucket (configured for static website hosting) or locally.
    - Open the page, create an annotation, and verify it’s saved in the Aurora database (use RDS Query Editor to check
      the `annotations` table).
- **Test the Lambda Function**:
    - Use the Lambda console to test with a sample annotation JSON (e.g.,
      `{ "id": "test-1", "body": [{"value": "Test comment"}] }`).
- **Verify Database**:
    - Query the `annotations` table:
      ```sql
      SELECT * FROM annotations LIMIT 5;
      ```

#### 7. **Cleanup**

- Delete resources to avoid costs:
    - Aurora cluster (RDS console).
    - Lambda function and API Gateway.
    - Secrets Manager secret.
    - S3 bucket (if used).

---

### Key Considerations

- **PostgreSQL vs. MySQL**:
    - **PostgreSQL** is recommended due to:
        - `jsonb` for efficient JSON storage and querying.
        - Full RDS Data API support for Serverless
          v2.[](https://dev.to/aws-builders/amazon-aurora-postgresql-now-supports-rds-data-api-51a1)
        - Better handling of complex annotation data (e.g., querying `content->>'creator'`).
    - **MySQL** limitations:
        - No RDS Data API support for Serverless v2 (requires provisioned instances or direct
          connections).[](https://dev.to/aws-builders/amazon-aurora-postgresql-now-supports-rds-data-api-51a1)
        - Weaker JSON support (less efficient for querying).
- **Cost Optimization**:
    - Aurora Serverless v2 scales to 0.5 ACUs when idle, minimizing costs.
    - Use AWS Free Tier or delete resources after testing to stay under $
      1.[](https://aws.amazon.com/pt/getting-started/hands-on/configure-connect-serverless-mysql-database-aurora/)
- **Scalability**:
    - Aurora Serverless v2 auto-scales based on load, handling thousands of
      annotations.[](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)
    - Lambda and API Gateway scale automatically with traffic.
- **Security**:
    - Use HTTPS for API Gateway.
    - Encrypt the Aurora cluster (enabled by default).
    - Restrict IAM permissions to least privilege.
- **Loading Annotations**:
    - To load annotations back into RecogitoJS, create another Lambda function and API endpoint to query the
      `annotations` table and return JSON to the client (e.g., `r.loadAnnotations(data)`).

---

### Example Annotation Storage

- **RecogitoJS Annotation (JSON)**:
  ```json
  {
    "@context": "http://www.w3.org/ns/anno.jsonld",
    "id": "anno-123",
    "type": "Annotation",
    "body": [{ "value": "This is a comment", "purpose": "commenting" }],
    "target": { "selector": { "type": "TextQuoteSelector", "exact": "Text to annotate" } }
  }
  ```
- **Stored in PostgreSQL**:
    - `annotation_id`: `anno-123`
    - `content`: (above JSON stored in `jsonb`)

---

### Troubleshooting

- **CORS Errors**: Ensure CORS is enabled in API Gateway (add `Access-Control-Allow-Origin: *` in responses).
- **Lambda Errors**: Check CloudWatch logs for issues (e.g., missing IAM permissions, incorrect ARNs).
- **Database Connectivity**: Verify security group rules and VPC settings.
- **RDS Data API Limits**: PostgreSQL doesn’t support enumerated types; ensure SQL is
  compatible.[](https://dev.to/aws-builders/amazon-aurora-postgresql-now-supports-rds-data-api-51a1)

---

### Further Customization

- **Query Annotations**: Add a `GET` endpoint to retrieve annotations by `annotation_id` or filter by `content` fields (
  e.g., `SELECT * FROM annotations WHERE content->>'creator' = 'user1'` in PostgreSQL).
- **Batch Inserts**: Modify the Lambda to handle multiple annotations using
  `batch-execute-statement`.[](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html)
- **Authentication**: Add Amazon Cognito to secure the API Gateway for user-specific annotations.

If you need help with specific steps (e.g., setting up the API Gateway, writing the `GET` endpoint, or deploying the
static site on S3), let me know, and I can provide additional artifacts or guidance!