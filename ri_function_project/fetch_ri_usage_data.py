import json
import os
import datetime
from azure.identity import ClientSecretCredential
from azure.mgmt.consumption import ConsumptionManagementClient

def fetch_ri_data():
    # Load SP credentials
    with open("sp_credentials.json") as f:
        creds = json.load(f)

    # Authenticate with Azure
    credential = ClientSecretCredential(
        tenant_id=creds["tenantId"],
        client_id=creds["clientId"],
        client_secret=creds["clientSecret"]
    )

    subscription_id = creds["subscriptionId"]
    consumption_client = ConsumptionManagementClient(credential, subscription_id)

    # Define date range (last 30 days)
    end_date = datetime.datetime.utcnow().date()
    start_date = end_date - datetime.timedelta(days=30)

    print(f"Fetching usage from {start_date} to {end_date}...")

    scope = f"/subscriptions/{subscription_id}"

    usage = consumption_client.usage_details.list(
        scope=scope,
        expand="properties/meterDetails"
    )

    ri_usage_data = []

    for item in usage:
        if item.reservation_id:
            ri_usage_data.append({
                "instanceName": item.instance_name,
                "reservationId": item.reservation_id,
                "cost": float(item.pretax_cost),
                "usageDate": str(item.date),
                "resourceType": item.meter_details.meter_category if item.meter_details else "Unknown"
            })

    output_file = "ri_usage_report.json"
    with open(output_file, "w") as f:
        json.dump(ri_usage_data, f, indent=2)

    print(f" RI usage data saved to {output_file}")
    return output_file

# Optional for local testing
if __name__ == "__main__":
    fetch_ri_data()
