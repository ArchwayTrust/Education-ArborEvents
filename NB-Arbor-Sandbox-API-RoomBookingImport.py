#!/usr/bin/env python
# coding: utf-8

# ## NB-Arbor-Sandbox-API-RoomBookingImport
# 
# New notebook

# # Room Booking Import

# ## Setup

# ### Imports

# In[1]:


from datetime import datetime, timedelta
import requests
import json
import time
import polars as pl


# ### Mounts

# In[2]:


notebookutils.fs.mount("abfss://Lakehouse_Dev@onelake.dfs.fabric.microsoft.com/LH_Raw.Lakehouse/Files/Arbor/", "/arbor_mnt")
mount_points = notebookutils.fs.mounts()
csv_path = next((mp["localPath"] for mp in mount_points if mp["mountPoint"] == "/arbor_mnt"), None)


# In[3]:


csv_path = f"{csv_path}/RoomBooking-Test.csv"


# ### API Setup

# In[4]:


username =  "ALTStaffUpdater"
password =  notebookutils.credentials.getSecret("https://altakv01.vault.azure.net/", "ArborStaffUpdaterPassword")
academy_url = "https://api-sandbox2.uk.arbor.sc"
rest_base_url = f"{academy_url}/rest-v2"  # Base URL for REST endpoints
graphql_url = f"{academy_url}/graphql/query"  # GraphQL endpoint


# In[5]:


request_headers = {"Accept": "application/json"}


# ## Key Functions

# In[6]:


def lookup_room_id(api_url, room_to_find):
    # Create the GraphQL query or mutation
    query = f"""
    {{
        Room(roomName: "{room_to_find}"){{
            id
            roomName
            shortName
                site{{
                    siteName
                }}
        }}
    }}
    """
    # Send the request
    response = requests.post(api_url, json={"query": query}, auth=(username, password))

    # Check response
    if response.status_code == 200:
        try:
            room_id = response.json()["data"]["Room"][0]["id"]
            return room_id
        except:
            raise RuntimeError("Room not found.")
    else:
        raise RuntimeError(f"Request failed with status code: {response.status_code}")


# In[7]:


def create_room_unavailability(rest_base_url, room_id, start_str, end_str, reason_str):
    api_url = f"{rest_base_url}/roomUnavailability"
    payload = {
        "request":
        {
            "roomUnavailability": 
                {
                    "room":
                        {
                            "entityType": 'Room',
                            "id": room_id,
                            "href": f"/rest-v2/rooms/{room_id}",
                        },
                    "startDatetime": start_str,
                    "endDatetime": end_str,
                    'reason': reason_str
                }
        }
    }

    response = requests.post(api_url, json=payload, auth=(username, password))

    return response


# ## School Event Types

# ### List Event Types

# In[93]:


api_url = f"{rest_base_url}/school-event-types/"
response = requests.get(api_url, auth=(username, password))
response.json()


# ### Get details of specific event type

# In[34]:


api_url = f"{rest_base_url}/school-event-types/DOBBS_EVENT_2"
response = requests.get(api_url, auth=(username, password))
response.json()


# ### Create an event type

# In[22]:


api_url = f"{rest_base_url}/school-event-types"
payload = {
    "request":
        {
            "schoolEventType": 
                {
                    "active": True,
                    "entityType": "SchoolEventType",
                    "code": "DOBBS EVENT 2",
                    "schoolEventTypeName": "Dobbs New Event Type 2"
                }
        }
    }

response = requests.post(api_url, json=payload, auth=(username, password))
response.text


# ### Edit an event type

# In[20]:


api_url = f"{rest_base_url}/school-event-types/DOBBS_EVENT_2"
payload = {
    "request":
        {
            "schoolEventType": 
                {
                    "active": True,
                    "href": "/rest-v2/school-event-types/DOBBS_EVENT_2",
                    "entityType": "SchoolEventType",
                    "code": "DOBBS EVENT",
                    "schoolEventTypeName": "Dobbs New Event Type"
                }
        }
    }

response = requests.put(api_url, json=payload, auth=(username, password))
response.text


# ### Disable an event type

# In[62]:


api_url = f"{rest_base_url}/school-event-types/DOBBS_EVENT_2"
payload = {
    "request":
        {
            "schoolEventType": 
                {
                    "active": True,
                    "href": "/rest-v2/school-event-types/DOBBS_EVENT_2"
                }
        }
    }

response = requests.put(api_url, json=payload, auth=(username, password))
response.text


# ### Delete event type

# In[36]:


response = requests.delete(f"{rest_base_url}/school-event-types/DOBBS_EVENT_2", json=payload, auth=(username, password))

response.text


# ## Find Person

# In[32]:


api_url = f"{rest_base_url}/email-addresses/158"
response = requests.get(api_url, auth=(username, password))
response.json()


# In[56]:


# Create the GraphQL query or mutation
query = f"""
{{
    EmailAddress(emailAddress: "bdobbs@Archwaytrust.co.uk", emailAddressType: "WORK"){{
        id
        emailAddress
        emailAddressType
        emailAddressOwner{{
            id
            entityType
        }}

    }}
}}
"""
# Send the request
response = requests.post(graphql_url, json={"query": query}, auth=(username, password))
response.json()


# In[58]:


# Convert JSON string to Python dictionary
data = response.json()

# Check for the Staff entityType and get the emailAddressOwner id
email_addresses = data["data"]["EmailAddress"]
for entry in email_addresses:
    if entry["emailAddressOwner"]["entityType"] == "Staff":
        email_owner_id = entry["emailAddressOwner"]["id"]
        print(f"Staff emailAddressOwner ID: {email_owner_id}")


# ## School Events

# In[39]:


api_url = f"{rest_base_url}/school-events"
payload = {
    "request":
        {
            "schoolEvent": 
                {
                    "entityType": "SchoolEvent",
                    "startDatetime": "2024-12-21 16:00:00",
                    "endDatetime": "2024-12-21 17:00:00",
                    "schoolEventType": {
                        "entityType": "SchoolEventType",
                        "href": "/rest-v2/school-event-types/GENERAL_EVENT"
                    },
                    "location": {
                        "entityType": "Room",
                        "href": "/rest-v2/rooms/96"
                    },
                    "schoolEventName": "Event Test 2",
                    "narrative": "BDobbs Test 2"
                }
        }
    }

response = requests.post(api_url, json=payload, auth=(username, password))


# In[40]:


response.text


# ### Find events of specific type and delete

# In[98]:


# Create the GraphQL query or mutation
query = f"""
{{
    SchoolEvent(schoolEventType__code: "USER__16818060778755"){{
        id
    }}
}}
"""
# Send the request
response = requests.post(graphql_url, json={"query": query}, auth=(username, password))


# In[99]:


response.json()


# In[96]:


data = response.json()
events = data.get('data', {}).get('SchoolEvent', [])  # Extract the list of events

# Iterate through each event and print the id
for event in events:
    event_id = event.get('id')  # Get the 'id'
    api_url = f"{rest_base_url}/school-events/{event_id}"
    response = requests.delete(api_url, auth=(username, password))
    print(response.status_code)


# In[27]:


response = requests.delete(f"{rest_base_url}/school-event-types/USER__16818060778755", auth=(username, password))

response.text


# ## Read CSV and Loop

# In[2]:


data = pl.read_csv(csv_path)

# Step 2: Iterate through each row
for row in data.iter_rows(named=True):  # named=True returns rows as dictionaries
    room_id = lookup_room_id(graphql_url, row["room_name"])
    #response = create_room_unavailability(rest_base_url, room_id, row["start_datetime"], row["end_datetime"], row["comment"])
    print(row["room_name"])

