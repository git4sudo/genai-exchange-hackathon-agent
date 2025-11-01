## **BigQuery Conversational Agent (Cloud Run MCP Server)**

This repository contains the necessary files to deploy a Model Context Protocol (MCP) server on Google Cloud Run that serves as a tool for a Vertex AI Agent to query BigQuery data.

### **1\. Prerequisites**

1. **Google Cloud Project**: A GCP project with Billing enabled.  
2. **APIs Enabled**: Ensure the **Cloud Run API** and **BigQuery API** are enabled.  
3. **BigQuery Data**: A BigQuery Dataset and Table populated with the data you want the agent to query.

### **2\. IAM Permissions (CRITICAL STEP)**

The Cloud Run service requires specific permissions to interact with BigQuery.

1. Find the **Service Account** associated with your Cloud Run service (e.g., \<PROJECT\_NUMBER\>-compute@developer.gserviceaccount.com or a custom service account).  
2. Grant this Service Account the following IAM roles on your Google Cloud Project:  
   * roles/bigquery.jobUser: Allows the service to run BigQuery queries (jobs).  
   * roles/bigquery.dataViewer: Allows the service to read data from the tables.

### **3\. Environment Variables**

Before building and deploying, update app.py or set these environment variables during the Cloud Run deployment:

| Variable | Description | Example |
| :---- | :---- | :---- |
| GCP\_PROJECT\_ID | Your Google Cloud Project ID. | my-data-project-12345 |
| BQ\_DATASET\_ID | The BigQuery dataset to target. | analytics\_data |
| BQ\_TABLE\_ID | The specific table to query. | monthly\_sales |

### **4\. Deployment Steps**

Use the Google Cloud CLI (gcloud) to build the container and deploy the service.

1. **Build the Container Image (using Cloud Build):**  
   gcloud builds submit \--tag gcr.io/${GCP\_PROJECT\_ID}/bq-agent-server

2. **Deploy to Cloud Run:**  
   * Set the region and service name.  
   * Crucially, set \--no-allow-unauthenticated to ensure only authorized Google services (like Vertex AI Agents) can call it.

gcloud run deploy bq-agent-server \\  
  \--image gcr.io/${GCP\_PROJECT\_ID}/bq-agent-server \\  
  \--platform managed \\  
  \--region us-central1 \\  
  \--memory 512Mi \\  
  \--set-env-vars GCP\_PROJECT\_ID=${GCP\_PROJECT\_ID},BQ\_DATASET\_ID=${BQ\_DATASET\_ID},BQ\_TABLE\_ID=${BQ\_TABLE\_ID} \\  
  \--no-allow-unauthenticated

### **5\. Integration with Vertex AI Agent**

After deployment, your Cloud Run service URL becomes the endpoint for your Model Context Protocol (MCP) Tool.

1. Go to **Vertex AI Agent Builder**.  
2. Create a new Tool or connect an existing Agent.  
3. When configuring the tool, point it to the **Cloud Run URL** and provide the necessary **OpenAPI/Tool Description** so the LLM knows how to convert a natural language request (e.g., "What was the total revenue?") into the expected JSON payload (e.g., {"query": "SELECT SUM(revenue) FROM monthly\_sales"}).

### Local development & fixing "Import 'fastapi' could not be resolved"

If your editor (VS Code) reports "Import 'fastapi' could not be resolved", it usually means the workspace Python interpreter isn't set to the virtual environment where the packages are installed. Follow these steps to set up a local virtual environment, install dependencies, and configure VS Code so imports resolve.

1. Create a virtual environment (from repository root):

```powershell
python -m venv .venv
```

2. Activate the venv in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; .\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. In VS Code: open the Command Palette (Ctrl+Shift+P) → "Python: Select Interpreter" → choose the interpreter:

```
<project-root>\.venv\Scripts\python.exe
```

   Then reload the window or restart the Python language server. The import resolution error should clear.

5. Run the app locally with uvicorn (after activating the venv):

```powershell
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

6. Notes on BigQuery credentials for local testing:
   - For local development, set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of a service account JSON key that has `BigQuery Data Viewer` and `BigQuery Job User` roles. Example:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\path\to\service-account.json'
```

   - If no credentials are available the app will still start, but BigQuery queries will fail and the app prints a warning. Use this only for local UI testing.

7. Quick import test (optional):

```powershell
python -c "import fastapi; print('fastapi', fastapi.__version__)"
```

If that prints a version number, the package is installed and the interpreter is correct.

Troubleshooting
- If VS Code still reports unresolved imports after selecting the interpreter, try: reload window (Ctrl+Shift+P → Developer: Reload Window) and ensure the "Python" extension is enabled.
- Make sure there are no global interpreter overrides in workspace settings (check `.vscode/settings.json`).

If you'd like, I can add this as a short CONTRIBUTING or dev-setup file — tell me where you'd prefer it.
