import json
from typing import List, Dict, Any
from src.loaders.base_loader import BaseLoader


class CSVLoader(BaseLoader):
    """Load CSV data into staging table"""

    def __init__(self):
        super().__init__("csv_file")

    def load(self, db, data: List[Dict[str, Any]], run_id: int) -> int:
        """Load CSV data to stg_csv_data table"""
        loaded_count = 0

        for record in data:
            try:
                query = """
                    INSERT INTO stg_csv_data (
                        source_file, row_number, raw_data, load_id
                    ) VALUES (%s, %s, %s, %s)
                """
                db.execute_query(
                    query,
                    (
                        record["source_file"],
                        record["row_number"],
                        json.dumps(record["data"]),
                        run_id
                    )
                )
                loaded_count += 1
                self.logger.debug(f"Loaded CSV row {record['row_number']}")

            except Exception as e:
                self.logger.error(
                    f"Failed to load CSV record row {record.get('row_number')}: {e}"
                )

        self.logger.info(f"Loaded {loaded_count}/{len(data)} CSV records")
        return loaded_count
