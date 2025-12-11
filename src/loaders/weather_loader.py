import json
from typing import List, Dict, Any
from src.loaders.base_loader import BaseLoader

class WeatherLoader(BaseLoader):
    def __init__(self):
        super().__init__("weather_api")
    
    def load(self, db, data: List[Dict[str, Any]], run_id: int) -> int:
        loaded_count = 0 
        
        for record in data:
            try:
                query = """
                    INSERT INTO stg_weather_data (
                    city, country, temperature, feels_like,
                    humidity, pressure, weather_condition,
                    wind_speed, raw_data, load_id
                ) VALUSES (%s, %s, %s,%s, %s, %s,%s, %s, %s, %s)
                """
                db.execute_query(
                    query,
                    (
                        record["city"],
                        record["country"],
                        record["temperature"],
                        record["feels_like"],
                        record["humidity"],
                        record["pressure"],
                        record["weather_condition"],
                        record["wind_speed"],
                        json.dumps(record["raw_data"]),
                        run_id
                    )
                )
                loaded_count += 1
                self.logger.debug(f"Loaded weather data for {record['city']}")
            except Exception as e:
                self.logger.error(f"Failed to load record for {record.get('city')}: {e}")

            self.logger.info(f"Loaded {loaded_count}/{len(data)} weather records")
            return loaded_count


            
