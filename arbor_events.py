import requests
import re

class ArborEvents:
    """Class to interact with Arbor Events API
    Attributes:
        base_url (str): Base URL of Arbor instance
        rest_url (str): Base URL for REST endpoints
        graphql_url (str): GraphQL endpoint
        auth (tuple): Arbor API username and password
    Methods:
        list_event_types: List all event types
        get_event_type: Get event type by code  
        create_event_type: Create a new event type
        disable_event_type: Disable an event type
        enable_event_type: Enable an event type
        delete_event_type: Delete an event type
        lookup_room_id: Based on room name lookup it's id
        create_room_unavailability: Create room unavailability
        lookup_email_owner_id: Lookup the owner of an email address
        list_school_events: List all school events
        create_school_event: Create a new school event
        delete_school_event: Delete a school event"""
    
    def __init__(self, base_url, username, password):
        """Initialize ArborEvents class
        Args:
            base_url (str): Base URL of Arbor instance
            username (str): Arbor API username
            password (str): Arbor API password
        Returns:
            None"""
        
        self.base_url = base_url
        self.rest_url = f"{base_url}/rest-v2"  # Base URL for REST endpoints
        self.graphql_url = f"{base_url}/graphql/query"  # GraphQL endpoint
        self.auth = (username, password)

    def _post_request(self, url, payload):
        response = requests.post(url, json=payload, auth=self.auth)
        if response.status_code == 201:
            return response.json()
        else:
            raise RuntimeError(f"Request failed. status_code: {response.status_code}, text: {response.text}")

    def _delete_request(self, url):
        response = requests.delete(url, auth=self.auth)
        if response.status_code == 204:
            return True
        else:
            raise RuntimeError(f"Request failed. status_code: {response.status_code}, text: {response.text}")

    def list_event_types(self):
        """List all event types
        Returns:
            response: Response object"""
        api_url = f"{self.rest_url}/school-event-types/"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def get_event_type(self, event_code):
        """Get event type by code
        Args:
            event_code (str): Event code
        Returns:
            response: Response object"""
        api_url = f"{self.rest_url}/school-event-types/{event_code}"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def create_event_type(self, event_code, event_name):
        """Create a new event type
        Args:
            event_code (str): Event code
            event_name (str): Event name
        Returns:
            response: Response object"""
        
        api_url = f"{self.rest_url}/school-event-types/"
        payload = {
            "request": {
                "schoolEventType": {
                    "active": True,
                    "entityType": "SchoolEventType",
                    "code": event_code,
                    "schoolEventTypeName": event_name
                }
            }
        }
        response = requests.post(api_url, json=payload, auth=self.auth)
        return response

    def disable_event_type(self, event_code):
        """Disable an event type
        Args:
            event_code (str): Event code
        Returns:
            response: Response object"""
        
        api_url = f"{self.rest_url}/school-event-types/{event_code}"
        payload = {
            "request": {
                "schoolEventType": {
                    "active": False,
                    "href": f"/rest-v2/school-event-types/{event_code}",
                    "entityType": "SchoolEventType"
                }
            }
        }
        response = requests.put(api_url, json=payload, auth=self.auth)
        return response.text
    
    def enable_event_type(self, event_code):
        """Enable an event type
        Args:
            event_code (str): Event code
        Returns:
            response: Response object"""
        
        api_url = f"{self.rest_url}/school-event-types/{event_code}"
        payload = {
            "request": {
                "schoolEventType": {
                    "active": True,
                    "href": f"/rest-v2/school-event-types/{event_code}",
                    "entityType": "SchoolEventType"
                }
            }
        }
        response = requests.put(api_url, json=payload, auth=self.auth)
        return response.text

    def delete_event_type(self, event_code):
        """Delete an event type
        Args:
            event_code (str): Event code
        Returns:
            response: Response object"""
        
        api_url = f"{self.rest_url}/school-event-types/{event_code}"
        response = requests.delete(api_url, auth=self.auth)
        return response.text
    
    def lookup_room_id(self, room_to_find):
        """Based on room name lookup it's id
        Args:
            room_to_find (str): Room name to search for
        Returns:
            room_id (str): Room id"""
        
        # Create the GraphQL query
        query = f"""
        {{
            Room(roomName: "{room_to_find}"){{
                id
            }}
        }}
        """
        # Send the request
        response = requests.post(self.graphql_url, json={"query": query}, auth=self.auth)

        # Check response
        if response.status_code == 200:
            try:
                room_id = response.json()["data"]["Room"][0]["id"]
                return room_id
            except:
                raise RuntimeError("Room not found.")
        else:
            raise RuntimeError(f"Request failed with status code: {response.status_code}")
        
    def create_room_unavailability(self, room_id, start_str, end_str, reason_str):
        """Create room unavailability.
        Args:
            room_id (str): Room id
            start_str (str): Start datetime in string format (e.g. "2024-12-21 16:00:00")
            end_str (str): End datetime in string format (e.g. "2024-12-21 17:00:00")
            reason_str (str): Reason for unavailability
        Returns:
            response: Response object"""

        api_url = f"{self.rest_url}/roomUnavailability"
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

        return self._post_request(api_url, payload)

    def lookup_email_owner_id(self, email_address, email_address_type="WORK"):
        """
        Lookup the owner of an email address
        Args:
            email_address (str): Email address to search for
            email_address_type (str): Email address type (default: "WORK")
        Returns:
            owner_id (str): Owner ID of the email address"""
        
        query = f"""
        {{
            EmailAddress(emailAddress: "{email_address}", emailAddressType: "{email_address_type}"){{
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
        response = requests.post(self.graphql_url, json={"query": query}, auth=self.auth)
        data = response.json()

        email_addresses = data["data"]["EmailAddress"]
        for entry in email_addresses:
            if entry["emailAddressOwner"]["entityType"] == "Staff":
                return entry["emailAddressOwner"]["id"]
        
        return None

    def list_school_events(self):
        """
        List all school events
        Returns:
            response: Response object"""
        
        api_url = f"{self.rest_url}/school-events/"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def create_school_event(self, event_name, start_datetime, end_datetime, event_type_href, location_href, narrative):
        """Create a new school event
        Args:
            event_name (str): Event name
            start_datetime (str): Start datetime in string format (e.g. "2024-12-21 16:00:00")
            end_datetime (str): End datetime in string format (e.g. "2024-12-21 17:00:00")
            event_type_href (str): Event type href
            location_href (str): Location href
            narrative (str): Event narrative
        Returns:
            href (str): Event href"""
        
        api_url = f"{self.rest_url}/school-events/"
        payload = {
            "request": {
                "schoolEvent": {
                    "entityType": "SchoolEvent",
                    "startDatetime": start_datetime,
                    "endDatetime": end_datetime,
                    "schoolEventType": {
                        "entityType": "SchoolEventType",
                        "href": event_type_href
                    },
                    "location": {
                        "entityType": "Room",
                        "href": location_href
                    },
                    "schoolEventName": event_name,
                    "narrative": narrative,
                    "active": True
                }
            }
        }
        data = self._post_request(api_url, payload)
        return data['schoolEvent']['href']

    def add_event_participant(self, event_href, participant_id, participant_type="Staff"):
        """Add a participant to an event.
        Args:
            event_href (str): Event href (returned when even created)
            participant_id (str): Participant ID
            participant_type (str): Type of participant (default is "Staff")
        Returns:
            bool: True if participant was added successfully, False otherwise
        """
        api_url = f"{self.rest_url}/eventParticipants"
        payload = {
            "request": {
                "eventParticipant": {
                    "entityType": "eventParticipant",
                    "event": {
                        "entityType": "SchoolEvent",
                        "href": event_href
                    },
                    "participant": {
                        "entityType": participant_type,
                        "href": f"/rest-v2/{participant_type}/{participant_id}"
                    }
                }
            }
        }
        self._post_request(api_url, payload)
        return True

    def delete_school_event(self, event_id):
        """Delete a school event
        Args:
            event_id (str): Event ID
        Returns:
            response: Response object"""
        
        api_url = f"{self.rest_url}/school-events/{event_id}"
        return self._delete_request(api_url)