"""
API extractor - extracts data from weather API
"""
import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from src.extractors.base_extractor import BaseExtractor

load_dotenv()


class WeatherAPIExtractor(BaseExtractor):
    """Extract weather data from OpenWeatherMap API"""
    
    def __init__(self, cities: List[str] = None):
        super().__init__("weather_api")
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url ="http://api.weatherapi.com/v1/current.json"

        if not self.api_key or self.api_key == "your_api_key_here":
            self.logger.warning("Weather API key not set.")

        cities_file = "paraguay_locations.txt"
        self.city_coords = self._load_cities_from_file(cities_file)

        if not self.city_coords:
            raise ValueError(f"No cities loaded from {cities_file}")

        self.logger.info(f"Loaded {len(self.city_coords)} Paraguay cities")

    def _load_cities_from_file(self, filepath: str) -> dict:
        import re

        cities = {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    match = re.search(
                        r'(\w+)\s*=\s*{latitud:\s*([-\d.]+),\s*longitud:\s*([-\d.]+)}',
                        line
                    )
                    if match:
                        city_name = match.group(1)
                        lat = float(match.group(2))
                        lon = float(match.group(3))
                        cities[city_name] = {
                            "lat": lat,
                            "lon": lon,
                            "country": "PY"
                        }
                        self.logger.debug(f"Loaded city: {city_name} ({lat}, {lon})")
        except FileNotFoundError:
            self.logger.error(f"Cities file not found: {filepath}")
            return {}
        return cities

    def extract(self) -> List[Dict[str, Any]]:
        """Extract weather data for configured cities"""
        data = []
        
        for city_name in self.city_coords.keys():
            try:
                weather_data = self._fetch_from_api(city_name)

                if weather_data:
                    data.append(weather_data)
                    self.logger.debug(f"Extracted weather data for {city_name}")

            except Exception as e:
                self.logger.error(f"Failed to extract data for {city_name}: {e}")
                continue
        
        return data
    
    def _fetch_from_api(self, city_name: str) -> Dict[str, Any]:
        coords = self.city_coords.get(city_name)

        if not coords:
            selc.logger.warning(f"Coordinates not found for {city_name}")
            return None

        lat = coords["lat"]
        lon = coords["lon"]
        query = f"{lat},{lon}"
        url = self.base_url

        params = {
            "key": self.api_key,
            "q": query,
            "aqi": "no"
        }

        self.logger.debug(f"Requesting weather for {city_name} at ({lat}, {lon})")
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()

        api_data = response.json()

        location = api_data["location"]
        current = api_data["current"]

        return {
            "city": location["name"],
            "country": location["country"],
            "temperature": current["temp_c"],
            "feels_like": current["feelslike_c"],
            "humidity": current["humidity"],
            "pressure": current["pressure_mb"],
            "weather_condition": current["condition"]["text"].lower(),
            "wind_speed": current["wind_kph"],
            "raw_data": api_data
        }
    
if __name__ == "__main__":
    # Test the extractor
    extractor = WeatherAPIExtractor()
    data = extractor.run()
    
    print(f"\nExtracted {len(data)} records:")
    for record in data:
        print(f"  {record['city']}: {record['temperature']}°C, {record['weather_condition']}")
