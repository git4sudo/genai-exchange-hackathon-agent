import os
import json
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError
import uvicorn

# --- Configuration (Replace with your BigQuery details) ---
# NOTE: The service account associated with the Cloud Run service must have 
# 'BigQuery Data Viewer' and 'BigQuery Job User' roles.
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id") 
DATASET_ID = os.environ.get("BQ_DATASET_ID", "your_dataset_id")
TABLE_ID = os.environ.get("BQ_TABLE_ID", "your_table_id")

# --- FastAPI Application Instance ---
app = FastAPI(
    title="BigQuery Agent MCP Server",
    description="A service to execute BigQuery SQL queries on behalf of a Vertex AI Agent."
)

# --- Pydantic Request Model for Agent Query ---
class AgentQueryRequest(BaseModel):
    """Schema for the incoming request payload from the LLM orchestrator."""
    query: str

# Initialize BigQuery Client
# This client will automatically use the credentials of the Cloud Run service account
try:
    BQ_CLIENT = bigquery.Client(project=PROJECT_ID)
    print(f"BigQuery Client initialized for Project: {PROJECT_ID}")
except Exception as e:
    # Print error but allow app to start for local testing without credentials
    print(f"Failed to initialize BigQuery Client: {e}")
    BQ_CLIENT = None


def execute_bigquery_query(query: str):
    """Executes a SQL query against BigQuery and returns the results."""
    if not BQ_CLIENT:
        # In a production environment, this should raise an exception
        return "Error: BigQuery client not initialized. Check service account permissions or configuration."

    print(f"Executing Query: {query}")
    
    # Simple guard against non-SELECT queries
    if not query.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed for data retrieval."}

    try:
        # Construct the fully qualified table name if the query doesn't specify it,
        # but typically the LLM generates the full query including project/dataset.
        query_job = BQ_CLIENT.query(query)
        
        # Waits for the job to complete
        results = query_job.result() 
        
        output_rows = []
        # Convert rows into a list of dictionaries
        # Use row.items() to get a dictionary representation of the row
        for row in results:
            output_rows.append(dict(row.items()))
        
        print(f"Query successful. Returned {len(output_rows)} rows.")
        return output_rows

    except GoogleAPICallError as e:
        error_message = f"BigQuery API Error: {e.errors[0]['message']}" if e.errors else str(e)
        print(f"BQ Execution Error: {error_message}")
        raise HTTPException(status_code=500, detail=f"BigQuery Error: {error_message}")
    except Exception as e:
        print(f"General Error during query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# --- Cloud Run Endpoint ---

@app.post("/", status_code=200)
async def agent_query(request_body: AgentQueryRequest):
    """
    Main endpoint for the Cloud Run service. It receives a structured SQL query 
    from the LLM orchestrator, executes it against BigQuery, and returns the results.
    """
    query = request_body.query
    
    # Execute the BigQuery query (the function now raises HTTPException on error)
    result = execute_bigquery_query(query)
        
    # If client wasn't initialized (e.g. local dev without credentials), check for string error
    if isinstance(result, str) and result.startswith("Error:"):
        raise HTTPException(status_code=500, detail=result)

    # FastAPI automatically handles converting the list/dict result to JSON
    return result

# Endpoint for health checks
@app.get("/health", status_code=200)
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "OK"}

if __name__ == "__main__":
    # Use uvicorn for local testing
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
