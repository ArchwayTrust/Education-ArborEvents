# pip install azure-identity azure-keyvault-secrets
# pip install polars

from azure.identity import InteractiveBrowserCredential
from azure.keyvault.secrets import SecretClient
from arbor_events import ArborEvents
import polars as pl

# Replace with url of Arbor instance
academy_url = "https://api-sandbox.uk.arbor.sc"

# Replace with your Key Vault URL
key_vault_url = "https://altakv01.vault.azure.net/"

# Create a credential using interactive browser authentication
credential = InteractiveBrowserCredential(additionally_allowed_tenants=["23990c89-ae67-4afc-87ce-470c97afeb37"])

# Create a SecretClient using the credential and Key Vault URL
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve a secret from the Key Vault
secret_name = "Arbor-SchoolEvents"
secret = secret_client.get_secret(secret_name)

# Initialize ArborEvents
arbor = ArborEvents(academy_url, "ALTSchoolEvents", secret.value)

# Load the CSV file
csv_file_path = "ExampleData.csv"
df = pl.read_csv(csv_file_path)

# Prepare a list to store the results
results = []

# Process each row in the CSV
for row in df.iter_rows(named=True):
    try:
        # Look up the room ID
        room_id = arbor.lookup_room_id(row['Room Name'])

        # Look up the staff ID if participant email is supplied
        staff_id = None
        if row['Participant Email']:
            staff_id = arbor.lookup_email_owner_id(row['Participant Email'])

        # Create the event
        event_href = arbor.create_school_event(
            start_datetime=row['Datetime From'],
            end_datetime=row['Datetime To'],
            event_type_code=row['Event Type'],
            room_id=room_id,
            event_name=row['Room Name'],
            narrative=row['Narrative']
        )

        # Add the participant if email is supplied
        if staff_id:
            arbor.add_event_participant(event_href, staff_id)

        # Append success result
        results.append({**row, "Status": "Success"})

    except Exception as e:
        # Append error result
        results.append({**row, "Status": f"Error: {str(e)}"})

# Save the results to a new CSV file
result_df = pl.DataFrame(results)
result_df.write_csv("room_bookings_results.csv")
