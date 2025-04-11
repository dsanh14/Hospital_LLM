# Hospital Operations Query System

A natural language interface for healthcare staff to query hospital operations data, providing accurate and explainable answers about ICU crowding, census trends, and other operational metrics.

## Current Data Structure

The system uses a SQLite database (`data/hospital.db`) with two main tables:

### ICU Statistics Table
```sql
icu_stats:
- unit_id (TEXT): Unique identifier for the ICU unit
- unit_name (TEXT): Name of the ICU unit (e.g., Medical ICU, Surgical ICU)
- total_beds (INTEGER): Total number of beds in the unit
- occupied_beds (INTEGER): Number of occupied beds
- timestamp (DATETIME): Time of the measurement
```

### Census Data Table
```sql
census:
- date (DATE): Date of the census
- unit_id (TEXT): Unit identifier
- patient_count (INTEGER): Number of patients
- admissions (INTEGER): Number of new admissions
- discharges (INTEGER): Number of discharges
```

## Features

- Natural language query interface for hospital operations data
- Support for common operational queries:
  - Current ICU occupancy rates
  - Census trends over time
  - Unit capacity analysis
- Built-in clarification mechanism for ambiguous queries
- Data visualization capabilities
- Comprehensive logging and feedback system

## Sample Queries

You can ask questions like:
- "What's the current ICU occupancy rate?"
- "Show me the census trends for the last month"
- "Which units are at capacity?"

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration:
# - Add your Gemini API key
# - Adjust model settings if needed
```

4. Run the application:
```bash
streamlit run src/main.py
```

## Project Structure

```
hospital_llm/
├── data/                   # Data storage
│   ├── hospital.db        # SQLite database
│   └── schema.json        # Data schema definition
├── src/                   # Source code
│   ├── data_layer/       # Database and data processing
│   ├── llm_layer/        # LLM integration and query processing
│   ├── clarification/    # Query ambiguity detection
│   └── utils/           # Utility functions
├── tests/                # Test suite
├── config/              # Configuration files
└── logs/               # Logging and feedback data
```

## Current Limitations

1. Using simulated test data:
   - 3 ICU units (Medical, Surgical, Cardiac)
   - 30 days of historical data
   - Randomly generated occupancy and census numbers

2. Query capabilities:
   - Limited to predefined query patterns
   - Basic time range support (e.g., "last month")
   - Simple statistical calculations

## Connecting to Real Data

To use this system with real hospital data:

1. Modify `src/data_layer/data_manager.py` to connect to your database
2. Update the schema in `data/schema.json` to match your data structure
3. Adjust SQL queries in `src/llm_layer/query_processor.py`
4. Add any additional security measures needed for healthcare data

## Inserting New Datasets

You can insert new datasets in several ways:

### Option 1: Direct SQL Database Replacement
1. Create your new SQLite database with the same schema:
```sql
CREATE TABLE icu_stats (
    unit_id TEXT,
    unit_name TEXT,
    total_beds INTEGER,
    occupied_beds INTEGER,
    timestamp DATETIME
);

CREATE TABLE census (
    date DATE,
    unit_id TEXT,
    patient_count INTEGER,
    admissions INTEGER,
    discharges INTEGER
);
```
2. Replace the existing `data/hospital.db` with your new database

### Option 2: Import from CSV/Excel
1. Place your data files in the `data` directory
2. Modify `src/data_layer/data_manager.py` to add an import method:
```python
def import_from_csv(self, table_name: str, file_path: str):
    df = pd.read_csv(file_path)
    with sqlite3.connect(self.db_file) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
```

### Option 3: Connect to External Database
1. Update the database configuration in `.env`:
```bash
DB_TYPE=postgresql  # or mysql, sqlserver, etc.
DB_HOST=your_host
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
```
2. Modify `src/data_layer/data_manager.py` to use SQLAlchemy for database connection:
```python
from sqlalchemy import create_engine

def __init__(self):
    db_url = f"{os.getenv('DB_TYPE')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    self.engine = create_engine(db_url)
```

### Requirements for New Datasets
1. Data must conform to the existing schema OR
2. Update the schema in `data/schema.json` to match your data structure
3. Ensure data types match (TEXT, INTEGER, DATETIME, etc.)
4. Update any custom SQL queries in `src/llm_layer/query_processor.py`

### Data Validation
The system includes built-in validation to ensure new data meets requirements:
```python
def validate_data(self, table_name: str, data: pd.DataFrame) -> bool:
    if table_name not in self.schema["tables"]:
        return False
    schema_columns = set(self.schema["tables"][table_name]["columns"].keys())
    data_columns = set(data.columns)
    return schema_columns.issubset(data_columns)
```

## Development

- Run tests: `pytest tests/`