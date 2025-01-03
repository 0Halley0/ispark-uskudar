import requests
from apscheduler.schedulers.background import BackgroundScheduler
import time
from math import radians, sin, cos, sqrt, atan2
import openrouteservice

# from app.models import ParkingLot
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


def get_parking_within_radius(lat, lng, radius=10, limit=20):

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
                    "freeTime": park["freeTime"],
                    "isOpen": park["isOpen"],
                    "distance": distance,
                }
            )

    nearby_parking_lots = sorted(nearby_parking_lots, key=lambda x: x["distance"])[
        :limit
    ]

    nearby_parking_cache[cache_key] = nearby_parking_lots

    return nearby_parking_lots


def get_drive_info(lat, lng, parking_lots):
    data = []

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

        data.append(
            {
                **park,
                "driveDistance": drive_distance,
                "driveTime": drive_time,
            }
        )

    return data


def get_parking_statistics():
    if not cached_ispark_data:
        logger.error("No İSPARK data available.")
        return {
            "totalParkingLots": 0,
            "totalCapacity": 0,
            "totalEmptyCapacity": 0,
            "districts": {},
        }

    total_parking_lots = 0
    total_capacity = 0
    total_empty_capacity = 0
    district_stats = {}

    for park in cached_ispark_data:
        district = park.get("district", "Unknown")
        capacity = int(park.get("capacity", 0))
        empty_capacity = int(park.get("emptyCapacity", 0))

        total_parking_lots += 1
        total_capacity += capacity
        total_empty_capacity += empty_capacity

        if district not in district_stats:
            district_stats[district] = {
                "parkingLots": 0,
                "capacity": 0,
                "emptyCapacity": 0,
            }

        district_stats[district]["parkingLots"] += 1
        district_stats[district]["capacity"] += capacity
        district_stats[district]["emptyCapacity"] += empty_capacity

    return {
        "totalParkingLots": total_parking_lots,
        "totalCapacity": total_capacity,
        "totalEmptyCapacity": total_empty_capacity,
        "districts": district_stats,
    }


def filter_parking_lots(empty_capacity=True, free_time=True):
    if not cached_ispark_data:
        logger.error("No İSPARK data available.")
        return []

    filtered_parking_lots = []

    for park in cached_ispark_data:
        if empty_capacity and int(park.get("emptyCapacity", 0)) <= 0:
            continue

        if free_time and int(park.get("freeTime", 0)) <= 0:
            continue


        filtered_parking_lots.append(park)

    return filtered_parking_lots
