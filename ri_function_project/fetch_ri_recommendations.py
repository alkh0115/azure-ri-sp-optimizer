import json
import requests

def get_azure_access_token():
    with open("sp_credentials.json") as f:
        creds = json.load(f)

    tenant_id = creds["tenantId"]
    client_id = creds["clientId"]
    client_secret = creds["clientSecret"]

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
    return access_token, creds["subscriptionId"]

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

    # Save to JSON file
    output_file = "ri_recommendations.json"
    with open(output_file, "w") as f:
        json.dump(recommendations, f, indent=2)

    print(f" RI/SP recommendations saved to {output_file}")
    return output_file

# Optional local test
if __name__ == "__main__":
    fetch_ri_recommendations()
