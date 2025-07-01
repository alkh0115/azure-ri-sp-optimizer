import os
from azure.storage.blob import BlobServiceClient

# Load connection string from environment
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not conn_str:
    raise Exception("Missing AZURE_STORAGE_CONNECTION_STRING environment variable.")

# Connect to Blob service
blob_service = BlobServiceClient.from_connection_string(conn_str)
container_name = "ri-reports"  # Ensure this container exists
blob_name = "ri_recommendations.json"
local_file = "ri_recommendations.json"

# Upload
with open(local_file, "rb") as data:
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)

print(f"\n Uploaded '{local_file}' to blob container '{container_name}' successfully.")
