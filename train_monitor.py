import requests
import time
from datetime import datetime, time as dt_time
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("RAILRADAR_API_KEY")
TRAIN_NUMBER = "15657"
STATION_CODE = "NOQ"

CHECK_INTERVAL = 5 * 60  # 5 minutes

START_TIME = dt_time(6, 15)
END_TIME = dt_time(8, 15)


def get_live_status():
    url = f"https://api.railradar.in/v1/trains/{TRAIN_NUMBER}/live"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def reached_station(data, station_code):

    for station in data["data"]["route"]:

        if station["stationCode"] != station_code:
            continue

        status = station["status"]

        if status == "reached":
            message = f"Train reached {station_code}"
            print(message)
            return message

        if status == "departed":
            arrival_time = station.get("actualArrival")
            departure_time = station.get("actualDeparture")

            message = (
                f"Train reached {station_code} "
                f"at {arrival_time} "
                f"and departed at {departure_time}"
            )

            print(message)
            return message

        if status == "upcoming":
            print(f"Train has not reached {station_code} yet")
            return None

    print(f"⚠️ Station {station_code} not found")
    return None


def announce(message):
    subprocess.run(
        [
            "/home/pranabsarma18/Desktop/train-notification/.venv/bin/python",
            "-m",
            "piper",
            "-m",
            "en_US-lessac-medium",
            "-f",
            "announcement.wav",
            "--",
            message,
        ]
    )

    subprocess.run(["aplay", "announcement.wav"])


def monitor():

    print("🚆 Train monitor started")

    while True:

        current_time = datetime.now().time()

        # Before 6:15 AM
        if current_time < START_TIME:
            print("Waiting for 6:15 AM...")
            time.sleep(30)
            continue

        # After 8:15 AM
        if current_time >= END_TIME:
            print("⏰ Monitoring window finished.")
            announce("Monitoring window finished")
            break

        try:
            print(f"\nChecking train at {datetime.now():%H:%M:%S}")
            announce(f"Checking train at {datetime.now():%H:%M:%S}")

            data = get_live_status()

            message = reached_station(data, STATION_CODE)
            if message:
                for _ in range(10):
                    announce(message)
                    time.sleep(2)
                break

            print("Next check in 5 minutes...")
            announce("Next check in 5 minutes")
            time.sleep(CHECK_INTERVAL)

        except requests.RequestException as error:
            print(f"❌ API error: {error}")
            announce(f"❌ API error: {error}")

            # Try again after 5 minutes
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    monitor()
