Construction Cost Estimator

FastAPI backend for estimating construction costs using live Eurostat data. Calculates project feasibility, loan requirements, and stores estimate history.

 Setup

```bash
pip install fastapi uvicorn requests
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` to test endpoints.

API

POST `/estimate`
```json
{
  "project_type": "house",
  "sq_meters": 150,
  "budget": 50000
}
```

Response: `total_cost`, `needs_loan`, `can_build`, `surplus`.

GET `/history` — all past estimates

GET `/rates` — current €/sqm rates

 Features

* Live Eurostat cost index integration
* Multi-project types (renovation, house, apartment, villa)
* Loan eligibility calculation (€100k cap)
* Estimate persistence to database
* Three-tier cache (memory → API → fallback)
* Input validation (positive values only)

Known Limits

* Import-time API fetch (cold start may lag)
* In-memory cache refreshes on restart only
* No async request handling
* No test coverage yet

## License

MIT
