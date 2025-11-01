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
