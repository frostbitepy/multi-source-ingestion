from abc import ABC, abstractmethod
from typing import List,Dict,Any
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseLoader(ABC):
    def __init__(self, loader_name: str):
        self.loader_name = loader_name
        self.logger = setup_logger(f"loader.{loader_name}")

    @abstractmethod
    def load(self, db, data: List[Dict[str, Any]], run_id: int) -> int:
        pass

    def create_pipeline_run(self, db, source_type: str) -> int:
        query = """
            INSERT INTO pipeline_runs (
                pipeline_name, source_type, status, start_time)
            VALUES (%s, %s, %s, %s)
            RETURNING run_id
        """
        result = db.execute_query(
            query,
            ("multi_source_ingestion", source_type, "running", datetime.now())
        )
        return result[0]["run_id"]

    def update_pipeline_run(
            self, db, run_id: int, status: str,
            recors_extracted: int = 0,
            records_loaded: int = 0,
            error_message: str = None):
        query = """
            UPTDATE pipeline_runs
            SET status = %s,
                end_time = %s,
                records_extracted = %s,
                error_message = %s
            WHERE run_id = %
        """
        db.execute_query(
            query,
            (status, datetime.now(), records_extracted, records_loaded,
             error_message, run_id)
        )

    def log_validation_errors(self, db, run_id: int,
                              invalid_records: list) -> int:
        import json
        logged_count = 0

        for invalid in invalid_records:
            try:
                record = invalid["record"]
                errors = invalid["errors"]

                query = """
                    INSERT INTO error_log (
                        run_id, source_type, error_type,
                        error_message, raw_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(
                    query,
                    (
                        run_id, slef.loader_name,"validation_error",
                        "; ".join(errors),
                        json.dumbs(record),
                        datetime.now()
                    )
                )
                logged_count += 1
            except Exception as e:
                self.logger.error(f"Failed to log error: {e}")
        return logged_count



