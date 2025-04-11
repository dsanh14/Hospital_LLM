import pandas as pd
import sqlite3
from typing import Dict, Any, Optional
import json
from pathlib import Path
import os
from datetime import datetime, timedelta
import numpy as np

class DataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.schema_file = self.data_dir / "schema.json"
        self.db_file = self.data_dir / "hospital.db"
        self.schema: Dict[str, Any] = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        self._load_schema()
        self._initialize_database()
    
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
                            "unit_id": {"type": "TEXT", "description": "Unique identifier for the ICU unit"},
                            "unit_name": {"type": "TEXT", "description": "Name of the ICU unit"},
                            "total_beds": {"type": "INTEGER", "description": "Total number of beds in the unit"},
                            "occupied_beds": {"type": "INTEGER", "description": "Number of occupied beds"},
                            "timestamp": {"type": "DATETIME", "description": "Time of the measurement"}
                        }
                    },
                    "census": {
                        "description": "Daily hospital census data",
                        "columns": {
                            "date": {"type": "DATE", "description": "Date of the census"},
                            "unit_id": {"type": "TEXT", "description": "Unit identifier"},
                            "patient_count": {"type": "INTEGER", "description": "Number of patients"},
                            "admissions": {"type": "INTEGER", "description": "Number of new admissions"},
                            "discharges": {"type": "INTEGER", "description": "Number of discharges"}
                        }
                    }
                }
            }
            self._save_schema()
    
    def _save_schema(self) -> None:
        """Save the current schema to schema.json"""
        with open(self.schema_file, 'w') as f:
            json.dump(self.schema, f, indent=2)
    
    def _initialize_database(self) -> None:
        """Initialize SQLite database and create tables if they don't exist"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Create tables based on schema
            for table_name, table_info in self.schema["tables"].items():
                columns = []
                for col_name, col_info in table_info["columns"].items():
                    columns.append(f"{col_name} {col_info['type']}")
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(columns)}
                )
                """
                cursor.execute(create_table_sql)
            
            # Add sample data if tables are empty
            self._add_sample_data(cursor)
            
            conn.commit()
    
    def _add_sample_data(self, cursor) -> None:
        """Add sample data to the tables if they're empty"""
        # Check if icu_stats is empty
        cursor.execute("SELECT COUNT(*) FROM icu_stats")
        if cursor.fetchone()[0] == 0:
            # Add sample ICU data
            icu_units = [
                ("ICU1", "Medical ICU", 20),
                ("ICU2", "Surgical ICU", 15),
                ("ICU3", "Cardiac ICU", 10)
            ]
            
            # Generate last 30 days of data
            for unit_id, unit_name, total_beds in icu_units:
                for days_ago in range(30):
                    date = datetime.now() - timedelta(days=days_ago)
                    occupied_beds = min(total_beds, int(np.random.normal(total_beds * 0.8, 2)))
                    cursor.execute(
                        "INSERT INTO icu_stats (unit_id, unit_name, total_beds, occupied_beds, timestamp) VALUES (?, ?, ?, ?, ?)",
                        (unit_id, unit_name, total_beds, occupied_beds, date.strftime("%Y-%m-%d %H:%M:%S"))
                    )
        
        # Check if census is empty
        cursor.execute("SELECT COUNT(*) FROM census")
        if cursor.fetchone()[0] == 0:
            # Add sample census data
            for days_ago in range(30):
                date = datetime.now() - timedelta(days=days_ago)
                for unit_id in ["ICU1", "ICU2", "ICU3"]:
                    patient_count = np.random.randint(8, 20)
                    admissions = np.random.randint(1, 5)
                    discharges = np.random.randint(1, 5)
                    cursor.execute(
                        "INSERT INTO census (date, unit_id, patient_count, admissions, discharges) VALUES (?, ?, ?, ?, ?)",
                        (date.strftime("%Y-%m-%d"), unit_id, patient_count, admissions, discharges)
                    )
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as a pandas DataFrame"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                return pd.read_sql_query(query, conn)
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the current schema"""
        return self.schema
    
    def get_table(self, table_name: str) -> Optional[pd.DataFrame]:
        """Get a specific table as a pandas DataFrame"""
        if table_name not in self.schema["tables"]:
            return None
        
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)
    
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