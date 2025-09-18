"""Query result processor"""

from typing import Dict, Any, List


class Processor:
    """
    Query result processor
    
    Processes raw database results into the expected format.
    """

    def process_select(self, query, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process select query results"""
        return results

    def process_insert_get_id(self, query, sql: str, values: List[Any], sequence: str = None) -> int:
        """Process insert and get ID"""
        # This will be implemented by specific database processors
        raise NotImplementedError("Subclasses must implement process_insert_get_id")

    def process_column_listing(self, results: List[Dict[str, Any]]) -> List[str]:
        """Process column listing results"""
        return [row['column_name'] for row in results]

    def process_columns(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process column information results"""
        return results