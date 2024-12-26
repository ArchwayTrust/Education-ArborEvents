# pip install azure-identity azure-keyvault-secrets
from azure.identity import InteractiveBrowserCredential
from azure.keyvault.secrets import SecretClient

# Replace with your Key Vault URL
key_vault_url = "https://altakv01.vault.azure.net/"

# Create a credential using interactive browser authentication
credential = InteractiveBrowserCredential(additionally_allowed_tenants=["23990c89-ae67-4afc-87ce-470c97afeb37"])

# Create a SecretClient using the credential and Key Vault URL
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve a secret from the Key Vault
secret_name = "ArborStaffUpdaterPassword"
secret = secret_client.get_secret(secret_name)