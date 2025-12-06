import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from src.extractors.base_extractor import BaseExtractor

class CSVExtractor(BaseExtractor):
    def __init__(self, file_path: str = None, data_folder: str = "data/raw"):
        super().__init__("csv_file")

        if file_path:
            self.file_path = Path(file_path)
        else:
            self.data_folder = Path(data_folder)
            self.file_path = None

    def find_csv_files(self) -> List[Path]:
        if not self.data_folder.exists():
            self.logger.warning(f"Data folder not found: {self.data_folder}")

            return []
        
        csv_files = list(self.data_folder.glob("*.csv"))
        self.logger.info(f"Found {len(csv_files)} CSV files in {self.data_folder}")

        return csv_files

    def read_csv_file(self, file_path: Path) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"Read {len(df)} rows from {file_path.name}")
            return df

        except UnicodeDecodeError:
            self.logger.warning(f"UTF-8 failed, trying latin-1 for {file_path.name}")
            df = pd.read_csv(file_path, encoding='latin-1')
            return df

        except Exception as e:
            self.logger.error(f"Failed to read {file_path.name}: {e}")
            raise

    def transform_dataframe_to_records(self, df: pd.DataFrame, source_file: str) -> List[Dict[str, Any]]:
        records = []

        for idx, row in df.iterrows():
            record = {
                "source_file": source_file,
                "row_number": idx + 2,
                "data": row.to_dict()
            }
            records.append(record)

        return records

    def extract(self) -> List[Dict[str, Any]]:
        all_records = []

        if self.file_path:
            files_to_process = [self.file_path]
        else:
            files_to_process = self.find_csv_files()

        if not files_to_process:
            self.logger.warning("No CSV files to process")
            return []

        for file_path in files_to_process:
            try:
                df = self.read_csv_file(file_path)
                records = self.transform_dataframe_to_records(df, file_path.name)
                all_records.extend(records)
                self.logger.info(f"Extracted {len(records)} records from {file_path.name}")

            except Exception as e:
                self.logger.error(f"Failed to process {file_path.name}: {e}")
                continue
        
        return all_records

if __name__ == "__main__":
         # Test the CSV extractor
         extractor = CSVExtractor()
         data = extractor.run()

         print(f"\n{'='*60}")
         print(f"Extracted {len(data)} total records")
         print(f"{'='*60}")

         if data:
             print("\nFirst record:")
             print(f"  Source: {data[0]['source_file']}")
             print(f"  Row: {data[0]['row_number']}")
             print(f"  Data: {data[0]['data']}")

             print("\nLast record:")
             print(f"  Source: {data[-1]['source_file']}")
             print(f"  Row: {data[-1]['row_number']}")
             print(f"  Data: {data[-1]['data']}")

