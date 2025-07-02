import json
from azure.identity import ClientSecretCredential

def get_azure_access_token():
    # Load credentials from JSON file
    with open("sp_credentials.json", "r") as file:
        creds = json.load(file)

    tenant_id = creds["tenantId"]
    client_id = creds["clientId"]
    client_secret = creds["clientSecret"]

    # Authenticate using ClientSecretCredential
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    # Get the access token for Azure Resource Manager
    token = credential.get_token("https://management.azure.com/.default")
    return token.token


if __name__ == "__main__":
    token = get_azure_access_token()
    print("Access token retrieved successfully!")
    print(token[:80] + "...")
