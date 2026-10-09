import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("WEATHER_API_KEY")


def get_current_weather(city_name: str) -> dict:
    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": API_KEY,
        "q": city_name
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print("WeatherAPI response:", response.text)
            return {"success": False, "error": f"HTTP {response.status_code}"}
        data = response.json()

        return {
            "success": True,
            "city": data["location"]["name"],
            "temperature": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "description": data["current"]["condition"]["text"]
        }

    except requests.exceptions.RequestException as err:
        return {"success": False, "error": str(err)}
    except (ValueError, KeyError) as err:
        return {
            "success": False,
            "error": f"Unexpected API response: {err}"
        }


if __name__ == "__main__":
    city = input("Enter a city: ")
    print(get_current_weather(city))

