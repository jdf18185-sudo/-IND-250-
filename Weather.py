import requests


def get_location_coordinates(city, state):
    """
    Get latitude and longitude for a given city and state using Open-Meteo Geocoding API.
    Ensures we search within the United States to avoid ambiguous locations.
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city,
            "admin1": state,
            "country": "United States",
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("results"):
            return None
        
        result = data["results"][0]
        return {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "name": result.get("name"),
            "admin1": result.get("admin1"),
            "country": result.get("country")
        }
    
    except requests.exceptions.Timeout:
        print("Error: Request timed out while searching for location.")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Connection error occurred while searching for location.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_weather_forecast(latitude, longitude):
    """
    Get 10-day weather forecast from Open-Meteo API.
    Returns temperature in Fahrenheit and precipitation in inches.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "timezone": "auto",
            "forecast_days": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.Timeout:
        print("Error: Request timed out while retrieving forecast.")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Connection error occurred while retrieving forecast.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def display_forecast(location_data, forecast_data):
    """
    Display the forecast in tabular format with location header.
    """
    location_name = f"{location_data['name']}, {location_data['admin1']}"
    print(f"\n--- 10-Day Forecast for {location_name} ---")
    print("Date | Max Temp | Min Temp | Rain")
    print("-" * 50)
    
    daily = forecast_data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]
    precipitation = daily["precipitation_sum"]
    
    for i in range(min(10, len(dates))):
        date = dates[i]
        max_temp = max_temps[i]
        min_temp = min_temps[i]
        rain = precipitation[i]
        
        print(f"{date} | {max_temp}°F | {min_temp}°F | {rain}inch")


def main():
    """
    Main function to run the weather forecast application.
    Prompts for city and state, retrieves forecast data, and displays results.
    """
    print("Welcome to the 10-Day Weather Forecast App")
    print("-" * 40)
    
    city = input("Enter city name: ").strip()
    state = input("Enter state name: ").strip()
    
    if not city or not state:
        print("Error: City and state cannot be empty.")
        return
    
    print(f"\nSearching for {city}, {state}...")
    
    # Get location coordinates
    location_data = get_location_coordinates(city, state)
    if not location_data:
        print(f"Error: Location '{city}, {state}' not found.")
        return
    
    print(f"Found: {location_data['name']}, {location_data['admin1']}")
    
    # Get weather forecast
    forecast_data = get_weather_forecast(location_data["latitude"], location_data["longitude"])
    if not forecast_data:
        print("Error: Failed to retrieve forecast data.")
        return
    
    # Display forecast
    display_forecast(location_data, forecast_data)


if __name__ == "__main__":
    main()
