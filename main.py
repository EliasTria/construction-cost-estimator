from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import save_estimate, get_recent_estimates
import finance

app = FastAPI(title="Construction Cost Estimator API", version="1.0.0")

class EstimateRequest(BaseModel):
    project_type: str
    sq_meters: float
    budget: float

class EstimateResponse(BaseModel):
    project_type: str
    sq_meters: float
    budget: float
    total_cost: float
    surplus: float
    needs_loan: bool
    can_build: bool

@app.get("/")
def root():
    return {"message": "Construction Cost Estimator API", "docs": "/docs"}

@app.post("/estimate", response_model=EstimateResponse)
def create_estimate(req: EstimateRequest):
    # Validate project type
    valid_types = ["renovation", "build_small", "house", "apartment", "villa"]
    if req.project_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid project_type. Choose from: {valid_types}")
    
    # Calculate using existing logic
    rate = finance.RATES[f"{req.project_type}_per_sqm"]
    total_cost = round(rate * req.sq_meters, 2)
    threshold = finance.CONFIG["loan_thresholds"][req.project_type]
    
    needs_loan = total_cost > req.budget
    shortfall = max(0, total_cost - req.budget)
    can_build = not needs_loan or shortfall <= 100000  # Max loan
    
    surplus = req.budget - total_cost
    
    # Save to DB if feasible
    if can_build:
        took_loan = needs_loan
        save_estimate(req.project_type, req.sq_meters, req.budget, total_cost, took_loan, surplus)
    
    return EstimateResponse(
        project_type=req.project_type,
        sq_meters=req.sq_meters,
        budget=req.budget,
        total_cost=total_cost,
        surplus=surplus,
        needs_loan=needs_loan,
        can_build=can_build
    )

@app.get("/history")
def get_history():
    rows = get_recent_estimates()
    return [
        {
            "id": r[0],
            "timestamp": r[1],
            "project_type": r[2],
            "sq_meters": r[3],
            "budget": r[4],
            "total_cost": r[5],
            "took_loan": bool(r[6]),
            "surplus": r[7]
        } for r in rows
    ]

@app.get("/rates")
def get_live_rates():
    return finance.RATES