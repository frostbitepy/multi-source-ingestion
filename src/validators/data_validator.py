from typing import Dict, Any, List, Tuple
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class WeatherDataValidator:
    def __init__(self):
        self.logger = setup_logger("validator.weather")
        self.validation_results = []

    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        required_fields = [
            "city", "country", "temperature", "humidity", "pressure", "wind_speed"
        ]

        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing or null field: {field}")

        if errors:
            return False, errors

        temperature = record.get("temperature")
        if temperature is not None:
            if not (-50 <= temperature <= 60):
                errors.append(f"Temperature out of range: {temperature}, expected -50 to 60)")

        humidity = record.get("humidity")
        if humidity is not None:
            if not (0 <= humidity <= 100):
                errors.append(f"Humidity out of range: {humidity}%, expected 0 to 100")

        wind_speed = record.get("wind_speed")
        if wind_speed is not None:
            if wind_speed < 0:
                errors.append(f"Negative wind speed: {wind_speed}")

        pressure = record.get("pressure")
        if pressure is not None:
            if pressure < 900 or pressure > 1100:
                errors.append(f"Pressure out of range: {pressure} hPa, expected 900 to 1100")

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid_records = []
        invalid_records = []

        for record in records:
            is_valid, errors = self.validate_record(record)

            if is_valid:
                valid_records.append(record)
                self.logger.debug(f"Valid record: {record['city']}")
            else:
                invalid_records.append({
                    "record": record,
                    "errors": errors
                })
                self.logger.warning(f"Invalid record: {record.get('city', 'unknown')} - {errors}")

        summary = {
            "total_records": len(records),
            "valid_count": len(valid_records),
            "invalid_count": len(invalid_records),
            "valid_records": valid_records,
            "invalid_records": invalid_records
        }

        self.logger.info(f"alidation complete: {summary['valid_count']}/{summary['total_records']} valid")

        return summary

if __name__ == "__main__":
    validator = WeatherDataValidator()

    test_records = [
             {
                 "city": "Encarnacion",
                 "country": "Paraguay",
                 "temperature": 35.1,
                 "feels_like": 33.8,
                 "humidity": 34,
                 "pressure": 1006,
                 "wind_speed": 7.2,
                 "weather_condition": "Sunny"
             },
             {
                 "city": "BadCity",
                 "country": "Paraguay",
                 "temperature": 150,  # Invalid - too hot!
                 "humidity": 34,
                 "pressure": 1006,
                 "wind_speed": 7.2,
                 "weather_condition": "Sunny"
             },
             {
                 "city": "NullCity",
                 "country": None,  # Invalid - missing country
                 "temperature": 25,
                 "humidity": 50,
                 "pressure": 1013,
                 "wind_speed": 5.0,
                 "weather_condition": "Clear"
             }
         ]

    results = validator.validate_batch(test_records)

    print(f"\n{'='*60}")
    print(f"Validation Results:")
    print(f"{'='*60}")
    print(f"Total records: {results['total_records']}")
    print(f"Valid: {results['valid_count']}")
    print(f"Invalid: {results['invalid_count']}")

    if results['invalid_records']:
        print(f"\nInvalid Records:")
        for invalid in results['invalid_records']:
            print(f"  - {invalid['record'].get('city', 'unknown')}:{invalid['errors']}")

