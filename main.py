from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import save_estimate, get_recent_estimates
import finance
from pydantic import BaseModel, Field



# 1. CREATE APP
app = FastAPI(title="Construction Cost Estimator API", version="1.0.0")

# 2. CORS MIDDLEWARE (MUST BE BEFORE ROUTES)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. MODELS
class EstimateRequest(BaseModel):
    project_type: str
    sq_meters: float = Field(gt=0, description="Must be positive")
    budget: float = Field(gt=0, description="Must be positive")

class EstimateResponse(BaseModel):
    project_type: str
    sq_meters: float
    budget: float
    total_cost: float
    surplus: float
    needs_loan: bool
    can_build: bool

# 4. ROUTES — all registered BEFORE the static mount
@app.post("/estimate", response_model=EstimateResponse)
def create_estimate(req: EstimateRequest):
    valid_types = ["renovation", "build_small", "house", "apartment", "villa"]
    if req.project_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid project_type. Choose from: {valid_types}")

    rate = finance.RATES[f"{req.project_type}_per_sqm"]
    total_cost = round(rate * req.sq_meters, 2)
    needs_loan = total_cost > req.budget
    shortfall = max(0, total_cost - req.budget)
    can_build = not needs_loan or shortfall <= 100000
    surplus = req.budget - total_cost

    if can_build:
        save_estimate(req.project_type, req.sq_meters, req.budget, total_cost, needs_loan, surplus)

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

app.mount("/", StaticFiles(directory="static", html=True), name="static")