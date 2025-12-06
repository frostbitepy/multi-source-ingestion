"""
Main pipeline orchestration
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

from src.utils.logger import setup_logger
from src.utils.db_connection import get_db_connection
from src.extractors.api_extractor import WeatherAPIExtractor
from src.validators.data_validator import WeatherDataValidator
from src.transformers.weather_transformer import WeatherTransformer

load_dotenv()
logger = setup_logger(__name__, log_level=os.getenv("LOG_LEVEL", "INFO"))


def create_pipeline_run(db, source_type: str) -> int:
    """Create a pipeline run record and return run_id"""
    query = """
        INSERT INTO pipeline_runs (
            pipeline_name, source_type, status, start_time
        ) VALUES (%s, %s, %s, %s)
        RETURNING run_id
    """
    result = db.execute_query(
        query,
        ("multi_source_ingestion", source_type, "running", datetime.now())
    )
    return result[0]["run_id"]


def update_pipeline_run(db, run_id: int, status: str, records_extracted: int = 0, 
                       records_loaded: int = 0, error_message: str = None):
    """Update pipeline run with results"""
    query = """
        UPDATE pipeline_runs 
        SET status = %s, 
            end_time = %s,
            records_extracted = %s,
            records_loaded = %s,
            error_message = %s
        WHERE run_id = %s
    """
    db.execute_query(
        query,
        (status, datetime.now(), records_extracted, records_loaded, error_message, run_id)
    )

def log_validation_errors(db, run_id: int, invalid_records: list) -> int:
    logged_count = 0

    for invalid in invalid_records:
        try:
            record = invalid["record"]
            errors = invalid["errors"]

            query = """
                INSERT INTO error_log (
                    run_id, source_type, error_type, error_message,
                    raw_data, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute_query(
                query,
                (
                    run_id,
                    "weather_api",
                    "validation_error",
                    "; ".join(errors),
                    json.dumps(record),
                    datetime.now()
                )
            )
            logged_count += 1
        except Exception as e:
            logger.error(f"Failed to log error for {record.get('city')}: {e}")

    return logged_count

def transform_to_production(db, run_id: int) -> dict[str, int]:
    logger.info("Starting transformation to produccion...")
    transformer = WeatherTransformer()
    stats = transformer.transform_and_load(db, run_id)
    logger.info(f"Trandformation complete:")
    logger.info(f" Transformed: {stats['records_transformed']} records")
    logger.info(f" Loaded: {stats['records_loaded']} records")

    return stats

def load_weather_data(db, data: list, run_id: int) -> int:
    """Load weather data into staging table"""
    loaded_count = 0
    
    for record in data:
        try:
            query = """
                INSERT INTO stg_weather_data (
                    city, country, temperature, feels_like, humidity, 
                    pressure, weather_condition, wind_speed, raw_data, load_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        except Exception as e:
            logger.error(f"Failed to load record for {record.get('city')}: {e}")
    
    return loaded_count

def run_weather_extraction():
         """Run the weather API extraction pipeline with validation"""
         logger.info("=" * 80)
         logger.info("Starting Multi-Source Data Ingestion Pipeline")
         logger.info("=" * 80)

         try:
             # Connect to database
             with get_db_connection() as db:
                 # Create pipeline run
                 run_id = create_pipeline_run(db, "weather_api")
                 logger.info(f"Created pipeline run ID: {run_id}")

                 try:
                     # Step 1: Extract data
                     extractor = WeatherAPIExtractor()
                     data = extractor.run()
                     logger.info(f"Extracted {len(data)} records")

                     # Step 2: Validate data (NEW!)
                     validator = WeatherDataValidator()
                     validation_results = validator.validate_batch(data)

                     logger.info(f"Validation complete:")
                     logger.info(f"  Valid: {validation_results['valid_count']}")
                     logger.info(f"  Invalid: {validation_results['invalid_count']}")

                     # Step 3: Log invalid records to error_log
                     if validation_results['invalid_count'] > 0:
                         error_count = log_validation_errors(
                             db,
                             run_id,
                             validation_results['invalid_records']
                         )
                         logger.warning(f"Logged {error_count} invalid records to error_log")

                     # Step 4: Load only valid data
                     logger.info(f"Loading {validation_results['valid_count']} valid records to database...")
                     loaded_count = load_weather_data(
                         db,
                         validation_results['valid_records'],  # Only valid records!
                         run_id
                     )

                     transform_stats = transform_to_production(db, run_id)

                     # Step 5: Update pipeline run
                     status = "success" if validation_results['invalid_count'] == 0 else "partial"
                     update_pipeline_run(
                         db, run_id, status,
                         records_extracted=len(data),
                         records_loaded=loaded_count
                     )

                     logger.info(f"Pipeline completed with status: {status}")
                     logger.info(f"  Extracted: {len(data)} records")
                     logger.info(f"  Valid: {validation_results['valid_count']} records")
                     logger.info(f"  Loaded: {loaded_count} records")
                     logger.info(f"  Failed: {validation_results['invalid_count']} records")

                 except Exception as e:
                     # Update pipeline run as failed
                     update_pipeline_run(db, run_id, "failed", error_message=str(e))
                     logger.error(f"Pipeline failed: {e}")
                     raise

         except Exception as e:
             logger.error(f"Fatal error: {e}")
             sys.exit(1)

         logger.info("=" * 80)

if __name__ == "__main__":
    run_weather_extraction()
