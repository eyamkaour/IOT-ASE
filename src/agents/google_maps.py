import logging
from state_graph import AgentState
from googleMaps.google_maps_client import gmaps_text_search_client
from googleMaps.maps import OSMTextSearchClient
from utils import prepaer_states
from langchain_core.messages import ToolMessage
def GoogleMaps(state: AgentState):
    logging.info("Using OpenStreetMap")

    # Vérifier si les coordonnées existent
    coordinates = state.get("location_finder_results", {}).get("coordinates") \
                  or state.get("coordinates")

    if not coordinates:
        return prepaer_states({
            "handled": [False],
            "node": ["GoogleMaps"],
            "context": "Missing coordinates",
            "call": "generator_agent"
        })

    query = state.get("query", "")

    if not query:
        return prepaer_states({
            "handled": [False],
            "node": ["GoogleMaps"],
            "context": "Error: query not provided",
            "call": "generator_agent"
        })

    # Instancier le client OpenStreetMap
    osm = OSMTextSearchClient()
    results = osm.text_search_with_details(
        query,
        coordinates[0],
        coordinates[1],
        limit=3
    )

    if results:
        return prepaer_states({
            "messages": [
                ToolMessage(
                    content=str(results),
                    name="GoogleMaps",
                    tool_call_id="call_IoT_engine"
                )
            ],
            "handled": [True],
            "node": ["GoogleMaps"],
            "context": str(results),
            "call": "generator_agent"
        })
    else:
        return prepaer_states({
            "handled": [False],
            "node": ["GoogleMaps"],
            "call": "generator_agent"
        })
