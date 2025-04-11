import pandas as pd
import os
from typing import Dict, Any, Optional
import json
from pathlib import Path

class DataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.schema_file = self.data_dir / "schema.json"
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.schema: Dict[str, Any] = {}
        
        self._load_schema()
        self._load_data()
    
    def _load_schema(self) -> None:
        """Load the data schema from schema.json"""
        if self.schema_file.exists():
            with open(self.schema_file, 'r') as f:
                self.schema = json.load(f)
        else:
            # Default schema if none exists
            self.schema = {
                "tables": {
                    "icu_stats": {
                        "description": "ICU statistics including occupancy and capacity",
                        "columns": {
                            "unit_id": {"type": "str", "description": "Unique identifier for the ICU unit"},
                            "unit_name": {"type": "str", "description": "Name of the ICU unit"},
                            "total_beds": {"type": "int", "description": "Total number of beds in the unit"},
                            "occupied_beds": {"type": "int", "description": "Number of occupied beds"},
                            "timestamp": {"type": "datetime", "description": "Time of the measurement"}
                        }
                    },
                    "census": {
                        "description": "Daily hospital census data",
                        "columns": {
                            "date": {"type": "date", "description": "Date of the census"},
                            "unit_id": {"type": "str", "description": "Unit identifier"},
                            "patient_count": {"type": "int", "description": "Number of patients"},
                            "admissions": {"type": "int", "description": "Number of new admissions"},
                            "discharges": {"type": "int", "description": "Number of discharges"}
                        }
                    }
                }
            }
            self._save_schema()
    
    def _save_schema(self) -> None:
        """Save the current schema to schema.json"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.schema_file, 'w') as f:
            json.dump(self.schema, f, indent=2)
    
    def _load_data(self) -> None:
        """Load all data files from the data directory"""
        for table_name in self.schema["tables"]:
            file_path = self.data_dir / f"{table_name}.csv"
            if file_path.exists():
                self.data_cache[table_name] = pd.read_csv(file_path)
    
    def get_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Get a specific table from the cache"""
        return self.data_cache.get(table_name)
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the current schema"""
        return self.schema
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a pandas query on the appropriate table"""
        # This is a placeholder - actual implementation would parse the query
        # and execute it on the appropriate table(s)
        raise NotImplementedError("Query execution not yet implemented")
    
    def add_data(self, table_name: str, data: pd.DataFrame) -> None:
        """Add new data to a table"""
        if table_name not in self.schema["tables"]:
            raise ValueError(f"Table {table_name} not found in schema")
        
        self.data_cache[table_name] = data
        data.to_csv(self.data_dir / f"{table_name}.csv", index=False)
    
    def validate_data(self, table_name: str, data: pd.DataFrame) -> bool:
        """Validate data against the schema"""
        if table_name not in self.schema["tables"]:
            return False
        
        schema_columns = set(self.schema["tables"][table_name]["columns"].keys())
        data_columns = set(data.columns)
        
        return schema_columns.issubset(data_columns) 