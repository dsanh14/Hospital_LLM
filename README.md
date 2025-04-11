# Hospital Operations Data Query System

A natural language interface for healthcare staff to query hospital operations data, providing accurate and explainable answers about ICU crowding, census trends, and other operational metrics.

## Features

- Natural language query interface for hospital operations data
- Support for ICU statistics, census trends, and operational metrics
- Explainable AI responses with data provenance
- Built-in clarification mechanism for ambiguous queries
- Comprehensive logging and feedback system

## Project Structure

```
hospital_llm/
├── data/                   # Data storage and schemas
├── src/                    # Source code
│   ├── data_layer/        # Data loading and processing
│   ├── llm_layer/         # LLM integration and prompting
│   ├── query_engine/      # Query translation and execution
│   ├── clarification/     # Ambiguity detection and clarification
│   └── utils/            # Utility functions
├── tests/                 # Test suite
├── config/               # Configuration files
└── logs/                 # Logging and feedback data
```

## Setup

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
# Edit .env with your configuration
```

## Usage

1. Start the application:
```bash
python src/main.py
```

2. Access the web interface at `http://localhost:8501`

## Development

- Run tests: `pytest tests/`
- Format code: `black src/`
- Lint code: `flake8 src/`

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.