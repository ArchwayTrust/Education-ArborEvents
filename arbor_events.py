import requests

class ArborEvents:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.rest_url = f"{base_url}/rest-v2"  # Base URL for REST endpoints
        self.graphql_url = f"{base_url}/graphql/query"  # GraphQL endpoint
        self.auth = (username, password)

    def list_event_types(self):
        api_url = f"{self.rest_url}/school-event-types/"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def get_event_type(self, event_code):
        api_url = f"{self.rest_url}/school-event-types/{event_code}"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def create_event_type(self, event_code, event_name):
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
        return response.text

    def disable_event_type(self, event_code):
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

        response = requests.post(api_url, json=payload, auth=self.auth)

        return response

    def find_person(self, person_id):
        api_url = f"{self.rest_url}/persons/{person_id}"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def list_school_events(self):
        api_url = f"{self.rest_url}/school-events/"
        response = requests.get(api_url, auth=self.auth)
        return response.json()

    def create_school_event(self, event_name, start_datetime, end_datetime, event_type_href, location_href, narrative):
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
        response = requests.post(api_url, json=payload, auth=self.auth)
        return response.text

    def delete_school_event(self, event_id):
        api_url = f"{self.rest_url}/school-events/{event_id}"
        response = requests.delete(api_url, auth=self.auth)
        return response.text

# Example usage:
# arbor = ArborEvents("https://your-base-url", "username", "password")
# print(arbor.list_event_types())
# print(arbor.get_event_type("DOBBS_EVENT_2"))
# print(arbor.create_event_type("DOBBS_EVENT_2", "Dobbs New Event Type 2"))
# print(arbor.edit_event_type("DOBBS_EVENT_2", "DOBBS_EVENT", "Dobbs New Event Type"))
# print(arbor.delete_event_type("DOBBS_EVENT_2"))
# print(arbor.find_person("12345"))
# print(arbor.list_school_events())
# print(arbor.delete_school_event("67890"))