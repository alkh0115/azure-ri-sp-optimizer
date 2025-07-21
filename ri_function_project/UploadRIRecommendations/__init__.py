import os
import json
import logging
import azure.functions as func
import requests
import csv
from io import StringIO, BytesIO
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from send_email import send_email_with_csv

def main(mytimer: func.TimerRequest) -> None:
    logging.info("RI Function Triggered: Starting fetch + upload + email pipeline...")

    try:
        # Step 1: Get Azure Access Token
        tenant_id = os.environ["TENANT_ID"]
        client_id = os.environ["CLIENT_ID"]
        client_secret = os.environ["CLIENT_SECRET"]
        subscription_id = os.environ["SUBSCRIPTION_ID"]

        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://management.azure.com/.default",
            "grant_type": "client_credentials"
        }

        token_response = requests.post(token_url, data=payload)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        # Step 2: Fetch RI/SP Recommendations
        url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/benefitRecommendations?api-version=2023-03-01"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("value", [])

        # Step 3: Build CSV content in memory
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow([
            "Subscription ID", "Resource Type", "Region", "Term", "Scope",
            "Recommended Quantity", "Current On-Demand Cost (Monthly)",
            "Estimated RI/SP Cost (Monthly)", "Estimated Savings (Monthly)",
            "Estimated Savings (%)", "Recommendation Type"
        ])

        for item in data:
            props = item.get("properties", {})
            writer.writerow([
                subscription_id,
                props.get("resourceType", ""),
                props.get("region", ""),
                props.get("term", ""),
                props.get("scope", ""),
                props.get("recommendedQuantity", ""),
                props.get("onDemandCost", {}).get("amount", ""),
                props.get("riRecommendedCost", {}).get("amount", ""),
                props.get("costSavings", {}).get("amount", ""),
                props.get("costSavings", {}).get("percentage", ""),
                props.get("category", "")
            ])

        csv_bytes = BytesIO(csv_buffer.getvalue().encode("utf-8"))
        csv_buffer.close()

        # Step 4: Upload to Blob Storage
        connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        container_name = "ri-reports"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
        blob_name = f"ri_recommendations_{timestamp}.csv"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(csv_bytes.getvalue(), overwrite=True)
        logging.info(f"Uploaded CSV to Blob: {blob_name}")

        # Step 5: Send email with attachment
        send_email_with_csv(csv_bytes.getvalue(), "alkh0115@algonquinlive.com")
        logging.info("Email sent successfully.")

    except Exception as e:
        logging.error(f"Error in RI Function: {str(e)}")
