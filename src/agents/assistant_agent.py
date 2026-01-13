import logging
from langchain_core.messages import SystemMessage, filter_messages
from state_graph import AgentState
from utils import parser, prepaer_states, get_thread
from agents_prompt import assistant_prompt


# == AJOUT IMPORTANT == #
# importer correctement GroqChat
from langchain_groq import ChatGroq
import os

# Lire les variables
groq_api_key = os.getenv("GROQ_API_KEY")

if groq_api_key is None:
    raise ValueError("❌ GROQ_API_KEY introuvable. Vérifie ton fichier .env !")

# Utilisation dans le LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=groq_api_key
)

# Geographic tools
from sensorsconnect_coverage.geography_db import check_city_country_exists
from sensorsconnect_coverage.location_finder import finder


def assistant_agent(state: AgentState):
    logging.info("entering assistant node")
    agent_state = {"node": ["assistant_agent"]}

    thread = get_thread(state)
    prompt = [SystemMessage(content=assistant_prompt)] + list(thread)

    #==============================#
    #   SÉCURISATION LLM INVOKE    #
    #==============================#
    try:
        response = llm.invoke(prompt)
        logging.info(response)

        # Tentative de parsing JSON
        response_json = parser.parse(response.content)

    except Exception as e:
        logging.error(f"Erreur LLM : {str(e)}")

        # Sécuriser : éviter UnboundLocalError
        safe_content = response.content if 'response' in locals() else "LLM error"

        # Valeur fallback pour éviter crash
        response_json = {
            "query-type": "greeting-general",
            "response": safe_content
        }

    #==========================================#
    #          ROUTAGE VERS AUTRES AGENTS      #
    #==========================================#
    if response_json["query-type"] == "service-recommendation":
        result = finder.process_location_query(response_json)
        logging.info(result)
        if result:
            # Forcer IoT-Engine pour toutes les villes de Tunisie
            if result["country"].lower() == "tunisia":
                logging.info("IoT_engine activated for Tunisia")
                agent_state["call"] = "IoT_engine"
                agent_state["query"] = response_json["question"]
            else:
                covered = check_city_country_exists(result["city"], result["country"])
                if covered:
                    logging.info("IoT_engine")
                    agent_state["call"] = "IoT_engine"
                    agent_state["query"] = response_json["question"]
                else:
                    logging.info("GoogleMaps")
                    agent_state["call"] = "GoogleMaps"
                    agent_state["query"] = response_json["question"]

  
    # Garder trace des messages
    agent_state["messages"] = [response] if "response" in locals() else []

    logging.info(agent_state)
    return prepaer_states(agent_state)
