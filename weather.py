import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("WEATHER_API_KEY")
if not API_KEY:
    raise RuntimeError("WEATHER_API_KEY is missing from .env")

def get_current_weather(city_name: str) -> dict:
    url = "https://api.weatherapi.com/v1/current.json"

    params = {
        "key": API_KEY,
        "q": city_name
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get(
                    "message", f"HTTP {response.status_code}"
                )
            except ValueError:
                error_message = f"HTTP {response.status_code}"

            return {"success": False, "error": error_message}
        data = response.json()

        location = data.get("location")
        current = data.get("current")

        if not isinstance(location, dict) or not isinstance(current, dict):
            return {
                "success": False,
                "error": "Missing location or current weather data."
            }

        condition = current.get("condition")

        if not isinstance(condition, dict):
            return {
                "success": False,
                "error": "Missing weather condition data."
            }

        required_fields = [
            location.get("name"),
            current.get("temp_c"),
            current.get("humidity"),
            condition.get("text")
        ]

        if any(value is None for value in required_fields):
            return {
                "success": False,
                "error": "Weather response contains missing fields."
            }

        return {
            "success": True,
            "city": location["name"],
            "temperature": current["temp_c"],
            "humidity": current["humidity"],
            "description": condition["text"]
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

