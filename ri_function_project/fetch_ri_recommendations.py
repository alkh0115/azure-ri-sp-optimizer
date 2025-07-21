import os
import json
import requests
import csv

def get_azure_access_token():
    try:
        # Try environment variables (production)
        tenant_id = os.environ["TENANT_ID"]
        client_id = os.environ["CLIENT_ID"]
        client_secret = os.environ["CLIENT_SECRET"]
        subscription_id = os.environ["SUBSCRIPTION_ID"]
    except KeyError:
        # Fallback to local file (development)
        with open("sp_credentials.json") as f:
            creds = json.load(f)

        tenant_id = creds["tenantId"]
        client_id = creds["clientId"]
        client_secret = creds["clientSecret"]
        subscription_id = creds["subscriptionId"]

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://management.azure.com/.default",
        "grant_type": "client_credentials"
    }

    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    return access_token, subscription_id

def fetch_ri_recommendations():
    access_token, subscription_id = get_azure_access_token()

    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}/providers/"
        f"Microsoft.CostManagement/benefitRecommendations?api-version=2023-03-01"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    print(f"Fetching RI/SP recommendations for subscription: {subscription_id}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    recommendations = response.json()
    data = recommendations.get("value", [])

    # Save as JSON (optional, for reference)
    with open("ri_recommendations.json", "w") as f:
        json.dump(recommendations, f, indent=2)

    # Save as CSV – always generate, even if empty
    csv_file = "ri_recommendations.csv"
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Subscription ID",
            "Resource Type",
            "Region",
            "Term",
            "Scope",
            "Recommended Quantity",
            "Current On-Demand Cost (Monthly)",
            "Estimated RI/SP Cost (Monthly)",
            "Estimated Savings (Monthly)",
            "Estimated Savings (%)",
            "Usage Patterns Analyzed",
            "Confidence Rating",
            "Offer ID",
            "Effective Date",
            "Recommendation Type"
        ])

        if data:
            for item in data:
                props = item.get("properties", {})
                writer.writerow([
                    subscription_id,
                    props.get("resourceType", ""),
                    props.get("region", ""),
                    props.get("term", ""),
                    props.get("scope", ""),
                    props.get("recommendedQuantity", ""),
                    f"${props.get('costWithNoReservedInstances', {}).get('amount', '')}",
                    f"${props.get('costWithReservedInstances', {}).get('amount', '')}",
                    f"${props.get('costSavings', {}).get('amount', '')}",
                    f"{props.get('costSavings', {}).get('percentage', '')}%",
                    props.get("usagePatternsAnalyzed", "N/A"),
                    props.get("confidenceRating", "N/A"),
                    props.get("offerId", "N/A"),
                    props.get("effectiveDate", "N/A"),
                    props.get("type", "")
                ])
        else:
            print(" No recommendations found. Empty CSV with headers created.")

    print(f" RI/SP recommendations saved to {csv_file}")
    return csv_file

# Optional local test
if __name__ == "__main__":
    fetch_ri_recommendations()
