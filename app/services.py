import requests
from apscheduler.schedulers.background import BackgroundScheduler

def fetch_ispark_data():
    url = "https://api.ibb.gov.tr/ispark/Park"
    params = {"district": "Üsküdar"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
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
