from datetime import datetime
from typing import Dict, Any, List
from src.utils.logger import setup_logger
from src.utils.db_connection import get_db_connection

logger = setup_logger(__name__)

class WeatherTransformer:

    def __init__(self):
        self.logger = setup_logger("transformer.weather")

    def transform_record(self, staging_record: Dict[str, Any]) -> Dict[str, Any]:
        production_record = {
            "city": staging_record["city"].upper(),
            "country": staging_record["country"],
            "temperature": round(staging_record["temperature"], 1),
            "feels_like": round(staging_record["feels_like"], 1),
            "humidity": staging_record["humidity"],
            "pressure": staging_record["pressure"],
            "weather_condition": staging_record["weather_condition"].lower(),
            "wind_speed": round(staging_record["wind_speed"], 1),
            "recorded_at": staging_record["extracted_at"],
            "loaded_at": datetime.now()
        }

        return production_record
    
    def get_staging_records(self, db, run_id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT
                id,city,country,temperature,feels_like,humidity,pressure,weather_condition,wind_speed,extracted_at,load_id
            FROM stg_weather_data
            WHERE load_id = %s
            ORDER BY extracted_at
        """
        
        records = db.execute_query(query, (run_id,))
        self.logger.info(f"Retrieved {len(records)} staging records for run_id {run_id}")

        return records

    def load_to_production(self, db, production_records: List[Dict[str, Any]]) -> int:
        loaded_count = 0

        for record in production_records:
            try:
                query = """
                    INSERT INTO weather_metrics (
                        city, country, temperature, feels_like, humidity,
                        pressure, weather_condition, wind_speed, recorded_at, loaded_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (city, country, recorded_at)
                    DO UPDATE SET
                        temperature = EXCLUDED.temperature,
                        feels_like = EXCLUDED.feels_like,
                        humidity = EXCLUDED.humidity,
                        pressure = EXCLUDED.pressure,
                        weather_condition = EXCLUDED.weather_condition,
                        wind_speed = EXCLUDED.wind_speed,
                        loaded_at = EXCLUDED.loaded_at
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
                        record["recorded_at"],
                        record["loaded_at"]
                    )
                )
                loaded_count += 1
            except Exception as e:
                self.logger.error(f"Failed to load record for {record['city']}: {e}")

        return loaded_count

    def transform_and_load(self, db, run_id: int) -> Dict[str, int]:
        self.logger.info(f"Starting transformation and loading for run_id {run_id}")

        staging_records = self.get_staging_records(db, run_id)

        if not staging_records:
            self.logger.warning(f"No staging records found for run_id {run_id}")
            return {"transformed_count": 0, "loaded_count": 0}

        production_records = []
        for record in staging_records:
            try:
                transformed = self.transform_record(record)
                production_records.append(transformed)
            except Exception as e:
                self.logger.error(f"Failed to transform record {record.get('city')}: {e}")

        self.logger.info(f"Transformed {len(production_records)} records for run_id {run_id}")

        loaded_count = self.load_to_production(db, production_records)
        self.logger.info(f"Loaded {loaded_count} records into production for run_id {run_id}")

        return {
            "records_transformed": len(production_records),
            "records_loaded": loaded_count
        }

if __name__ == "__main__":
    from src.utils.db_connection import get_db_connection
    transformer = WeatherTransformer()

    with get_db_connection() as db:
        result = db.execute_query("""
            SELECT run_id
            FROM pipeline_runs
            WHERE source_type = 'weather_api'
            AND status IN ('success', 'partial')
            ORDER BY start_time DESC
            LIMIT 1
        """
        )
        
        if result:
            run_id = result[0]['run_id']
            print(f"Transforming data from run_id: {run_id}")
            stats = transformer.transform_and_load(db, run_id)
            print(f"\nTransformation complete:")
            print(f"  Transformed: {stats['records_transformed']} records")
            print(f"  Loaded: {stats['records_loaded']} records")
        else:
            print("No successful pipeline runs found. Run the extraction first.")
    
