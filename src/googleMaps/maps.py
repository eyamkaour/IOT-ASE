import requests

class OSMTextSearchClient:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.osrm_url = "http://router.project-osrm.org/table/v1/driving/"

    def text_search(self, query, limit=4):
        params = {
            'q': query,
            'format': 'json',
            'addressdetails': 1,
            'limit': limit,
        }
        headers = {
            'User-Agent': 'MyApp/1.0 (contact@example.com)'  # OBLIGATOIRE POUR NOMINATIM
        }
        
        response = requests.get(self.nominatim_url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_travel_times(self, origin_latitude, origin_longitude, destinations):
        coords = f"{origin_longitude},{origin_latitude};" + ";".join(
            f"{lon},{lat}" for lat, lon in destinations
        )
        url = f"{self.osrm_url}{coords}"
        params = {'annotations': 'duration'}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            durations = data.get('durations', [[]])[0][1:]  # skip origin→origin
            travel_times = [duration / 60 for duration in durations] 
            return travel_times
        
        return ['N/A'] * len(destinations)

    def text_search_with_details(self, query, origin_latitude, origin_longitude, limit=4):
        places = self.text_search(query, limit)
        
        destinations = [
            (float(place['lat']), float(place['lon']))
            for place in places
        ]

        # Travel time
        travel_times = self.get_travel_times(origin_latitude, origin_longitude, destinations)
        
        places_with_details = []
        for place, ttime in zip(places, travel_times):
            name = place.get('display_name', 'N/A')
            address = place.get('display_name', 'N/A')

            places_with_details.append({
                'entity_name': name,
                'address': address,
                'rate': 'N/A (OSM n’a pas les ratings)',
                'estimated_travel_time': f"{ttime:.2f} mins" if ttime != 'N/A' else 'N/A'
            })
        
        return places_with_details


# Example usage
osm_client = OSMTextSearchClient()
results = osm_client.text_search_with_details("coffee shop Istanbul", 48.8566, 2.3522)
print(results)
