import time
import os
from datetime import datetime
import requests

# TTC NextBus/Umo platform configurations for Kennedy Subway Station
# Agency tag for Toronto Transit Commission is 'ttc'
API_URL = "https://webservices.nextbus.com/service/publicJSONFeed"
PARAMS = {
    "command": "predictions",
    "a": "ttc",
    "stopId": "14457"  # Unique transit stop identifier for Kennedy Subway Platforms
}

def clear_screen():
    """Keeps the command terminal clean and looking like a dispatch monitor."""
    os.system('cls' if os.name == 'nt' else 'clear')

def fetch_kennedy_predictions():
    try:
        response = requests.get(API_URL, params=PARAMS, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Communication error with TTC server (Status: {response.status_code})")
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"📡 Connection dropped. Re-routing tracking sequence... ({e})")
        return None

def display_live_board():
    clear_screen()
    print("=" * 60)
    print(f" 🏙️  KENNEDY STATION — REAL-TIME SUBWAY DISPATCH MONITOR")
    print(f" Live Feed Active • Last Synchronized: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    print(f"{'ROUTE / DIRECTION':<35} | {'ARRIVING IN':<20}")
    print("-" * 60)

    data = fetch_kennedy_predictions()
    if not data or "predictions" not in data:
        print("⏳ Waiting for active telemetry from incoming trains...")
        return

    predictions_data = data["predictions"]
    
    # NextBus packages responses differently if there is 1 route vs multiple routes active
    if isinstance(predictions_data, dict):
        predictions_list = [predictions_data]
    else:
        predictions_list = predictions_data

    found_trains = False

    for route_info in predictions_list:
        route_title = route_info.get("routeTitle", "TTC Subway Line")
        direction_info = route_info.get("direction")

        if not direction_info:
            continue

        # Can return a single dict direction block or a list of direction blocks
        if isinstance(direction_info, dict):
            direction_list = [direction_info]
        else:
            direction_list = direction_info

        for direction in direction_list:
            dir_title = direction.get("title", "Incoming Train")
            prediction_items = direction.get("prediction")

            if not prediction_items:
                continue

            if isinstance(prediction_items, dict):
                prediction_items = [prediction_items]

            # Grab the next top 3 arrivals for the platform
            for pred in prediction_items[:3]:
                minutes = int(pred.get("minutes", 0))
                
                # Format time text for a clean UI
                if minutes == 0:
                    time_display = "列車 ARRIVING NOW 🚇"
                elif minutes == 1:
                    time_display = "1 minute"
                else:
                    time_display = f"{minutes} minutes"

                # Standardize displaying Line 2 vs Line 5 routes out of Kennedy
                display_title = f"{route_title} ({dir_title})"
                print(f"{display_title:<35} | {time_display:<20}")
                found_found_trains = True

    if not found_trains:
        print("💤 No scheduled trains are currently reporting GPS hooks near the terminal yards.")
    
    print("=" * 60)
    print("🔄 Dispatch board auto-updates every 30 seconds. [Ctrl + C to Exit]")

# Active Loop Engine
if __name__ == "__main__":
    try:
        while True:
            display_live_board()
            time.sleep(30)  # Rate limit safety to keep your connection to the feed clear
    except KeyboardInterrupt:
        print("\n🪙 Tracking campaign closed. Safe travels out there in the GTA!")
