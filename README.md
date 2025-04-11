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

## Development

- Run tests: `pytest tests/`
- Format code: `black src/`
- Lint code: `flake8 src/`

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.