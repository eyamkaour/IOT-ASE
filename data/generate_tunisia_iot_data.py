"""
generate_tunisia_iot_data.py

Ce script génère un dossier `data/` contenant des fichiers JSON prêts à importer
dans MongoDB Atlas. Les données sont réalistes et localisées sur **toute la Tunisie**.

Collections générées :
- car_rental, parking, gas_station, charging_station, restaurants,
  pharmacy, hospitals, shopping_mall, supermarket, atm, hotel,
  laundry, gym, bus_stop, coffee_shop
- collections supplémentaires pour une base plus vaste :
  taxi_stand, car_wash, library, school, university, hospital_specialty,
  pharmacy_24h, bank, atm_24h, cinema, park, police_station,
  fire_station, post_office, hotel_luxury, hostel, coworking_space,
  sport_facility, museum, bus_station

Chaque fichier contient 25 documents par collection (modifiable).

--- Utilisation ---
1) Installer les dépendances :
   pip install pymongo

2) Générer les fichiers JSON :
   python generate_tunisia_iot_data.py
   Cela crée ./data/<collection>.json pour toutes les collections

3) Importer dans MongoDB Atlas (optionnel) :
   export MONGODB_URL="mongodb+srv://..."
   python generate_tunisia_iot_data.py --import

Note : le script lit la variable d'environnement MONGODB_URL si --import est demandé.
"""

import os
import json
import random
import argparse
from math import cos, sin
from datetime import datetime

# --- Configuration ---
OUTPUT_DIR = "data"
NUM_PER_COLLECTION = 25

# Coordonnées des 24 gouvernorats tunisiens
CITIES = {
    "Tunis": (36.8065, 10.1815),
    "Ariana": (36.8983, 10.1900),
    "Ben Arous": (36.7725, 10.2350),
    "Manouba": (36.8110, 10.0940),
    "Nabeul": (36.4520, 10.7360),
    "Zaghouan": (36.4010, 10.1470),
    "Bizerte": (37.2746, 9.8739),
    "Beja": (36.7333, 9.1833),
    "Jendouba": (36.5030, 8.7800),
    "Kef": (36.1667, 8.7167),
    "Siliana": (36.0833, 9.3667),
    "Sousse": (35.8256, 10.6330),
    "Monastir": (35.7770, 10.8260),
    "Mahdia": (35.5040, 11.0620),
    "Sfax": (34.7406, 10.7603),
    "Kairouan": (35.6781, 10.0963),
    "Kasserine": (35.1670, 8.8370),
    "Sidi Bouzid": (35.0366, 9.4589),
    "Gabes": (33.8815, 10.0990),
    "Mednine": (33.3540, 10.5020),
    "Tataouine": (32.9297, 10.4510),
    "Gafsa": (34.4250, 8.7842),
    "Tozeur": (33.9197, 8.1333),
    "Kebili": (33.7042, 8.9692)
}

# Collections à générer
COLLECTIONS = [
    "car_rental", "parking", "gas_station", "charging_station",
    "restaurants", "pharmacy", "hospitals", "shopping_mall",
    "supermarket", "atm", "hotel", "laundry", "gym",
    "bus_stop", "coffee_shop",
    # nouvelles collections
    "taxi_stand", "car_wash", "library", "school", "university",
    "hospital_specialty", "pharmacy_24h", "bank", "atm_24h", "cinema",
    "park", "police_station", "fire_station", "post_office",
    "hotel_luxury", "hostel", "coworking_space", "sport_facility",
    "museum", "bus_station"
]

# Préfixes et suffixes pour noms réalistes
BUSINESS_PREFIXES = [
    "Centre", "Clinique", "Pharmacie", "Station", "Parking", "Espace",
    "Café", "Restaurant", "Hôtel", "Garage", "Agence", "Bazar", "Carrefour",
    "Salon", "Boutique", "Services"
]

BUSINESS_SUFFIXES = [
    "El Medina", "La Corniche", "Les Jardins", "Sidi Bou", "Habib", "El Aziz",
    "City", "Express", "Central", "Plaza", "Royal", "Nord", "Sud", "Est", "Ouest"
]

STREET_NAMES = [
    "Avenue Hédi Nouira", "Rue Habib Bourguiba", "Avenue Bourguiba", "Rue de la Liberté",
    "Avenue Taieb Mhiri", "Rue Jebel Jloud", "Avenue de France", "Rue Ibn Khaldoun",
    "Avenue Mohamed V", "Rue du 7 Novembre"
]

SERVICE_TYPES_MAP = {col: col for col in COLLECTIONS}

random.seed(42)

# --- Fonctions auxiliaires ---

def jitter_coord(lat, lon, radius_m=3000):
    """Ajoute un petit décalage aléatoire autour du centre de la ville."""
    r = random.random() * radius_m
    theta = random.random() * 2 * 3.14159265359
    dlat = (r * sin(theta)) / 111000.0
    dlon = (r * cos(theta)) / (111000.0 * cos(lat * 3.14159265359 / 180.0))
    return round(lon + dlon, 6), round(lat + dlat, 6)


def random_rating():
    return round(random.uniform(2.8, 5.0), 1)


def random_address(city):
    street = random.choice(STREET_NAMES)
    n = random.randint(1, 200)
    return f"{n} {street}, {city}, Tunisia"


def random_name(col):
    pref = random.choice(BUSINESS_PREFIXES)
    suf = random.choice(BUSINESS_SUFFIXES)
    if col == "car_rental": return f"{pref} Rent-a-Car {suf}"
    if col in ("restaurants", "coffee_shop"): return f"{pref} {suf} Café"
    if col == "pharmacy" or col == "pharmacy_24h": return f"Pharmacie {suf}"
    if col in ("hospitals", "hospital_specialty"): return f"Clinique {suf}"
    if col in ("hotel", "hotel_luxury"): return f"Hôtel {suf}"
    return f"{pref} {suf}"


def make_document(collection, city):
    lat0, lon0 = CITIES[city]
    lon, lat = jitter_coord(lat0, lon0, radius_m=7000)
    doc = {
        "Service Name": random_name(collection),
        "Service Address": random_address(city),
        "Service Type": SERVICE_TYPES_MAP.get(collection, collection),
        "rating": random_rating(),
        "location": {"type": "Point", "coordinates": [lon, lat]},
        "phone": "+216" + str(random.randint(20000000, 29999999)),
        "city": city,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    if collection == "car_rental": doc.update({"fleet_size": random.randint(5, 100), "price_per_day": round(random.uniform(20, 120), 2)})
    if collection == "charging_station": doc.update({"connectors": random.choice(["Type2", "CCS", "CHAdeMO"])})
    if collection == "gas_station": doc.update({"has_shop": random.choice([True, False])})
    return doc


def generate_all(output_dir=OUTPUT_DIR, per_collection=NUM_PER_COLLECTION):
    os.makedirs(output_dir, exist_ok=True)
    summary = {}
    for col in COLLECTIONS:
        docs = [make_document(col, random.choice(list(CITIES.keys()))) for _ in range(per_collection)]
        path = os.path.join(output_dir, f"{col}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        summary[col] = path
    return summary


def import_to_mongodb(mongodb_url, dbname="IoT-Engine"):
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure
    
    try:
        # Add connection options for better reliability
        client = MongoClient(
            mongodb_url, 
            tls=True,
            retryWrites=True,
            w='majority',
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection first
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas successfully!")
        
        db = client[dbname]
        
        for col in COLLECTIONS:
            path = os.path.join(OUTPUT_DIR, f"{col}.json")
            if not os.path.exists(path): 
                print(f"⚠️  File not found: {path}")
                continue
                
            with open(path, "r", encoding="utf-8") as f:
                docs = json.load(f)
                if docs:
                    # Use try-except for collection operations
                    try:
                        # Drop collection if exists
                        if col in db.list_collection_names():
                            db[col].drop()
                        
                        # Insert documents
                        result = db[col].insert_many(docs)
                        print(f"✅ Imported {len(result.inserted_ids)} docs into {dbname}.{col}")
                        
                    except Exception as e:
                        print(f"❌ Error importing {col}: {e}")
        
        print("🎉 Import finished successfully!")
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Check your internet connection and MongoDB Atlas IP whitelist")
    except OperationFailure as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Check your username/password and database user permissions")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate Tunisia IoT data and optionally import into MongoDB")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import into MongoDB")
    parser.add_argument("--num", type=int, default=NUM_PER_COLLECTION, help="Number of docs per collection")
    args = parser.parse_args()

    print("Generating data...")
    summary = generate_all(per_collection=args.num)
    print("Generated files:")
    for k, v in summary.items(): print(f" - {k}: {v}")

    if args.do_import:
        mongodb_url = os.environ.get("MONGODB_URL")
        print("mongo url")
        print(mongodb_url)
        if not mongodb_url:
            print("MONGODB_URL not set. Set and re-run with --import")
            return
        import_to_mongodb(mongodb_url)
        print("importation fini")


if __name__ == "__main__":
    main()
