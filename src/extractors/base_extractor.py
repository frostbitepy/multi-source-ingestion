"""
Base extractor class that all extractors inherit from
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for all extractors"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.extracted_data = []
        self.extraction_time = None
        self.logger = setup_logger(f"extractor.{source_name}")
    
    @abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from source
        Must be implemented by child classes
        
        Returns:
            List of dictionaries containing extracted data
        """
        pass
    
    def run(self) -> List[Dict[str, Any]]:
        """
        Run the extraction process
        
        Returns:
            Extracted data
        """
        self.logger.info(f"Starting extraction from {self.source_name}")
        self.extraction_time = datetime.now()
        
        try:
            self.extracted_data = self.extract()
            self.logger.info(
                f"Extraction complete: {len(self.extracted_data)} records from {self.source_name}"
            )
            return self.extracted_data
        except Exception as e:
            self.logger.error(f"Extraction failed for {self.source_name}: {e}")
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get extraction metadata"""
        return {
            "source_name": self.source_name,
            "extraction_time": self.extraction_time,
            "record_count": len(self.extracted_data)
        }
