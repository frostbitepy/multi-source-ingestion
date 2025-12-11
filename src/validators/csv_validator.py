from typing import Dict, Any, List, Tuple
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CSVDataValidator:
    def __init__(self):
        self.logger = setup_logger("validator.csv")

    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        data = record.get("data", {})
        required_fields = ["date", "product", "category", "amount", "quantity", "region"]

        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        try:
            datetime.strptime(str(data["date"]), "%Y-%m-%d")
        except ValueError:
            errors.append(f"Invalid date format: {data['date']} (expected YYYY-MM-DD)")

        try: 
            amount = float(data["amount"])
            if amount <= 0:
                errors.append(f"Amount must be positive: {amount}")
        except (ValueError, TypeError):
            errors.append(f"Amount must be a number: {data['amount']}")

        try:
            quantity = int(data["quantity"])
            if quantity <= 0:
                errors.append(f"Quantity must be positive: {quantity}")
        except (ValueError, TypeError):
            errors.append(f"Quantity must be a number: {data['quantity']}")

        if not str(data.get("category", "")).strip():
            errors.append("Category cannot be empty")
        
        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid_records = []
        invalid_records = []

        for record in records:
            is_valid, errors = self.validate_record(record)

            if is_valid:
                valid_records.append(record)
                self.logger.debug(f"Valid record: row {record.get('row_numbre')}")
            else:
                invalid_records.append({
                    "record": record,
                    "errors": errors
                })
        summary = {
            "total_records": len(records),
            "valid_count": len(valid_records),
            "invalid_count": len(invalid_records),
            "valid_records": valid_records,
            "invalid_records": invalid_records
        }

        self.logger.info(f"Validation complete: {summary['valid_count']}/{summary['total_records']} valid")

        return summary

if __name__ == "__main__":
         # Test the validator
         validator = CSVDataValidator()

         test_records = [
             {
                 "source_file": "test.csv",
                 "row_number": 2,
                 "data": {
                     "date": "2024-12-01",
                     "product": "Laptop",
                     "category": "Electronics",
                     "amount": 1200.50,
                     "quantity": 2,
                     "region": "Asuncion"
                 }
             },
             {
                 "source_file": "test.csv",
                 "row_number": 3,
                 "data": {
                     "date": "invalid-date",  # Invalid
                     "product": "Mouse",
                     "category": "",  # Invalid - empty
                     "amount": -25.99,  # Invalid - negative
                     "quantity": 5,
                     "region": "Encarnacion"
                 }
             }
         ]

         results = validator.validate_batch(test_records)

         print(f"\n{'='*60}")
         print(f"Validation Results:")
         print(f"{'='*60}")
         print(f"Total: {results['total_records']}")
         print(f"Valid: {results['valid_count']}")
         print(f"Invalid: {results['invalid_count']}")

         if results['invalid_records']:
             print(f"\nInvalid Records:")
             for invalid in results['invalid_records']:
                 print(f"  Row {invalid['record']['row_number']}: {invalid['errors']}")
