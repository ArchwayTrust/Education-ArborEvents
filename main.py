# pip install azure-identity azure-keyvault-secrets
# pip install polars

from azure.identity import InteractiveBrowserCredential
from azure.keyvault.secrets import SecretClient
from arbor_events import ArborEvents

# Replace with url of Arbor instance
academy_url = "https://api-sandbox2.uk.arbor.sc"

# Replace with your Key Vault URL
key_vault_url = "https://altakv01.vault.azure.net/"

# Create a credential using interactive browser authentication
credential = InteractiveBrowserCredential(additionally_allowed_tenants=["23990c89-ae67-4afc-87ce-470c97afeb37"])

# Create a SecretClient using the credential and Key Vault URL
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve a secret from the Key Vault
secret_name = "ArborStaffUpdaterPassword"
secret = secret_client.get_secret(secret_name)

arbor = ArborEvents(academy_url, "ALTStaffUpdater", secret.value)

event_types = arbor.list_event_types()

print(event_types)