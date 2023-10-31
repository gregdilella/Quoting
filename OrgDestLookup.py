import googlemaps
import requests
import json

def get_route_details(Org, Dest, api_key):
    gmaps = googlemaps.Client(key=api_key)

    def calculate_mileage_and_tolls(origin, destination):
        try:
            directions = gmaps.directions(origin, destination, units='imperial', avoid='ferries')
            if directions:
                distance = directions[0]['legs'][0]['distance']['text']
                tolls_found = any("toll" in step.get('html_instructions', '').lower() for step in directions[0]['legs'][0]['steps'])
                tolls = "Tolls found on this route." if tolls_found else "No tolls found on this route."
                origin_lat = directions[0]['legs'][0]['start_location']['lat']
                origin_lng = directions[0]['legs'][0]['start_location']['lng']
                destination_lat = directions[0]['legs'][0]['end_location']['lat']
                destination_lng = directions[0]['legs'][0]['end_location']['lng']
                dest_state = directions[0]['legs'][0]['end_address'].split(',')[-2].strip()
                org_state = directions[0]['legs'][0]['start_address'].split(',')[-2].strip()
                return distance, tolls, (origin_lat, origin_lng), (destination_lat, destination_lng), org_state, dest_state
            else:
                return "No directions found for the given origin and destination."
        except Exception as e:
            return str(e)

    mileage, tolls, (origin_lat, origin_lng), (destination_lat, destination_lng), org_state, dest_state = calculate_mileage_and_tolls(Org, Dest)

    endpoint = 'https://routes.googleapis.com/directions/v2:computeRoutes'
    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lng
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination_lat,
                    "longitude": destination_lng
                }
            }
        },
        "travelMode": "DRIVE",
        "extraComputations": ["TOLLS"],
        "routeModifiers": {
            "vehicleInfo": {
                "emissionType": "GASOLINE"
            },
            "tollPasses": ["US_MA_EZPASSMA", "US_WA_GOOD_TO_GO"]
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.travelAdvisory.tollInfo,routes.legs.travelAdvisory.tollInfo'
    }
    response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    response_json = response.json()
    mileage = response_json['routes'][0]['distanceMeters'] / 1609.34
    estimated_toll = response_json['routes'][0]['legs'][0]['travelAdvisory']['tollInfo']['estimatedPrice'][0]
    
    return mileage, estimated_toll, org_state, dest_state

# Example usage:
api_key = 'AIzaSyD6W8IlU0bOU1xZCrQx3zD9UUkoQ6TU_Bk'
Org = "SFO"
Dest = "LAX"
mileage, estimated_toll, org_state, dest_state = get_route_details(Org, Dest, api_key)
print(mileage, estimated_toll, org_state, dest_state)