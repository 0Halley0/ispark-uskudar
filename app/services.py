import requests
from apscheduler.schedulers.background import BackgroundScheduler
import time
from math import radians, sin, cos, sqrt, atan2
import openrouteservice
from config import Config
import logging

logger = logging.getLogger(__name__)

ORS_CLIENT = openrouteservice.Client(key=Config.OPENROUTESERVICE_API_KEY)

cached_ispark_data = None
nearby_parking_cache = {}

def fetch_ispark_data():
    global cached_ispark_data

    url = "https://api.ibb.gov.tr/ispark/Park"
    params = {"district": "Üsküdar"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        """ for park in data:
            park["lat"] = float(park["lat"])
            park["lng"] = float(park["lng"])

        ParkingLot.update_or_insert(data) """

        cached_ispark_data = data
        print("Fetched data successfully:", data[:5])
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching İSPARK data: {e}")
        return None


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_ispark_data, "interval", minutes=5)
    scheduler.start()
    print("Scheduler started, fetching data every 5 minutes.")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_parking_within_radius(lat, lng, radius=5, limit=10):

    cache_key = (round(lat, 4), round(lng, 4))

    if cache_key in nearby_parking_cache:
        return nearby_parking_cache[cache_key]

    if not cached_ispark_data:
        logger.error("No İSPARK data available.")
        return []

    nearby_parking_lots = []
    for park in cached_ispark_data:
        park_lat = float(park["lat"])
        park_lng = float(park["lng"])

        distance = haversine(lat, lng, park_lat, park_lng)
        if distance <= radius:
            nearby_parking_lots.append(
                {
                    "parkID": park["parkID"],
                    "parkName": park["parkName"],
                    "lat": park_lat,
                    "lng": park_lng,
                    "capacity": park["capacity"],
                    "emptyCapacity": park["emptyCapacity"],
                    "workHours": park["workHours"],
                    "parkType": park["parkType"],
                    "district": park["district"],
                    "distance": distance,
                }
            )

    nearby_parking_lots = sorted(nearby_parking_lots, key=lambda x: x["distance"])[
        :limit
    ]

    nearby_parking_cache[cache_key] = nearby_parking_lots

    return nearby_parking_lots


def get_drive_info(lat, lng, parking_lots):
    enriched_parking_lots = []

    for park in parking_lots:
        try:
            coords = [[lng, lat], [park["lng"], park["lat"]]]
            response = ORS_CLIENT.directions(
                coordinates=coords, profile="driving-car", format="geojson"
            )
            route = response["features"][0]["properties"]["segments"][0]
            drive_distance = route["distance"] / 1000
            drive_time = route["duration"] / 60
        except openrouteservice.exceptions.ApiError as e:
            logger.error(f"ORS API error for park {park['parkName']}: {e}")
            drive_distance = None
            drive_time = None

        enriched_parking_lots.append(
            {
                **park,
                "driveDistance": drive_distance,
                "driveTime": drive_time,
            }
        )

    return enriched_parking_lots
