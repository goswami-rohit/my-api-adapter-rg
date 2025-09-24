import httpx
import time
import sys
import uvicorn
from fastmcp import FastMCP

# The number of times to retry fetching the OpenAPI spec
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 5

openapi_spec = None
for i in range(MAX_RETRIES):
    try:
        print(f"Attempt {i + 1}/{MAX_RETRIES}: Fetching OpenAPI spec...")
        # Get the response object first to handle potential errors
        response = httpx.get("https://myserverbymycoco.onrender.com/openapi.json")
        response.raise_for_status()  # This will raise an exception for 4xx or 5xx errors
        response.encoding = 'utf-8' # Ensure the response is decoded as UTF-8
        openapi_spec = response.json()
        print("✅ Successfully fetched and decoded OpenAPI spec.")
        break  # Exit the loop if successful
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        print(f"❌ Error fetching OpenAPI spec: {e}")
        if i < MAX_RETRIES - 1:
            print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
        else:
            print("❌ All retry attempts failed. Exiting.")
            sys.exit(1) # Exit with an error status

# Ensure openapi_spec was successfully fetched before proceeding
if openapi_spec is None:
    print("❌ Critical: OpenAPI spec could not be loaded. Aborting.")
    sys.exit(1)

# Create the MCP server instance
mcp_app = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=httpx.AsyncClient(base_url="https://myserverbymycoco.onrender.com"),
    name="My API Server"
)

# Render's environment variable for the web server port
# Use a default of 8000 if not set
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
host = "0.0.0.0"

# Use uvicorn to run the FastMCP application
if __name__ == "__main__":
    print(f"🚀 Starting uvicorn server on http://{host}:{port}")
    uvicorn.run(mcp_app, host=host, port=port)
