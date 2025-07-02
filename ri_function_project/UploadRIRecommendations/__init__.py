import os
import json
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from datetime import datetime

def main(mytimer: func.TimerRequest) -> None:
    logging.info("RI Upload function triggered...")

    # Path to the JSON file generated from fetch_ri_recommendations.py
    local_file_path = os.path.join(os.getcwd(), "ri_recommendations.json")

    if not os.path.exists(local_file_path):
        logging.error(f"File not found: {local_file_path}")
        return

    # Read file contents
    with open(local_file_path, "r") as f:
        recommendations = f.read()

    # Connect to Blob Storage
    connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    container_name = "ri-reports"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    blob_name = f"ri_recommendations_{timestamp}.json"

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        blob_client.upload_blob(recommendations, overwrite=True)
        logging.info(f"Uploaded {blob_name} to container '{container_name}'.")
    except Exception as e:
        logging.error(f"Upload failed: {str(e)}")
