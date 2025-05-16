# Property Management API

A REST API for property management data analysis developed using FastAPI and SQLite.

## Setup and Installation

1. Clone the repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Make sure the CSV files are placed in the `data/` directory:
   - leases.csv
   - properties.csv
   - units.csv

4. Seed the database:
```bash
python seed_db.py
```

5. Run the API:
```bash
uvicorn app.main:app --reload
```

6. Access the API documentation at: http://localhost:8000/docs

## Architecture and Design Decisions

- **Framework**: FastAPI for its high performance, ease of use, and built-in documentation.
- **Database**: SQLite for simplicity and ease of setup, suitable for demonstration purposes.
- **ORM**: SQLAlchemy for database interactions, providing a clean abstraction layer.
- **Query Approach**: Used a combination of SQLAlchemy ORM queries and raw SQL for more complex analyses.
- **API Design**: RESTful endpoints with clear naming conventions and appropriate response schemas.

## Extensibility and Scalability

- **Modular Design**: Separation of concerns between models, schemas, and database logic.
- **API Versioning**: Can be easily implemented when needed.
- **Database Migration**: Structure allows for easy migration to more robust databases like PostgreSQL if needed.
- **Containerization**: Can be containerized using Docker for easy deployment.

## Sample JSON Responses

### Quarterly Occupancy Rates
```json
{
  "property_id": 1,
  "property_name": "Property_1",
  "quarterly_rates": [
    {
      "quarter": "Q1",
      "occupancy_rate": 0.85
    },
    {
      "quarter": "Q2",
      "occupancy_rate": 0.92
    },
    {
      "quarter": "Q3",
      "occupancy_rate": 0.78
    },
    {
      "quarter": "Q4",
      "occupancy_rate": 0.88
    }
  ]
}
```

### Average Lease Duration
```json
{
  "property_id": 1,
  "property_name": "Property_1",
  "average_lease_duration_days": 248.5
}
```

## Assumptions

- Date format in CSV files is DD/MM/YYYY.
- Property IDs are unique and correspond properly between tables.
- A unit can have multiple leases but should ideally not have overlapping active leases.
- Quarterly calculations are based on calendar quarters.