import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

def load_static_config(path="config.json"):
    """Load committed configuration (endpoints, multipliers, fallbacks)."""
    with open(path) as f:
        return json.load(f)

def get_live_rates(config):
    """Fetch live construction cost index → calculate real €/sqm rates."""
    cache_path = Path(config["cache_file"])
    
    # Check cache freshness
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                cached = json.load(f)
            age = datetime.now() - datetime.fromisoformat(cached["fetched_at"])
            if age < timedelta(hours=config["cache_ttl_hours"]):
                print(f"[CACHE] Using rates from {cached['fetched_at']}")
                return cached["rates"]
        except (json.JSONDecodeError, KeyError, ValueError):
            pass  # Corrupt cache, refetch
    
    # Fetch live from Eurostat
    try:
        resp = requests.get(
            config["api_url"],
            params=config["api_params"],
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        
        # TODO: Adjust key path based on actual API response
        values = list(data["value"].values())
        latest_change = float(values[-1])
        current_index = 100 * (1 + latest_change / 100)
        
        base_rate = config["base_rate_per_sqm"] * (current_index / config["base_index_value"])
        
        rates = {
            f"{ptype}_per_sqm": round(base_rate * mult, 2)
            for ptype, mult in config["rate_multipliers"].items()
        }
        
        # Cache result
        with open(cache_path, "w") as f:
            json.dump({
                "rates": rates,
                "index_value": current_index,
                "fetched_at": datetime.now().isoformat()
            }, f)
        
        print(f"[LIVE] Index: {current_index} | Base rate: €{base_rate:.2f}/sqm")
        return rates
        
    except Exception as e:
        print(f"[FALLBACK] API failed ({e}). Using calibrated defaults.")
        return {
            f"{k}_per_sqm": round(v * config["base_rate_per_sqm"], 2)
            for k, v in config["rate_multipliers"].items()
        }

# Module-level initialization
STATIC_CONFIG = load_static_config()
RATES = get_live_rates(STATIC_CONFIG)
CONFIG = STATIC_CONFIG

def display_estimate_summary(project_type , sq_meters , budget):
    rate = RATES[f"{project_type}_per_sqm"]
    total_cost = round(rate * sq_meters, 2)
    threshold = CONFIG["loan_thresholds"][project_type]

    print(f"\n ESTIMATE SUMMARY")
    print(f"   Project:      {project_type.title()}")
    print(f"   Size:         {sq_meters} sqm")
    print(f"   Rate:         €{rate:,.2f}/sqm")
    print(f"   Total Cost:   €{total_cost:,.2f}")
    print(f"   Budget:       €{budget:,.2f}")
    
    if budget >= total_cost:
        print(f"Surplus:   €{budget - total_cost:,.2f}")
    else:
        print(f"   Shortfall: €{total_cost - budget:,.2f}")
    
    needs_loan = total_cost > budget
    shortfall = max(0, total_cost - budget)
    max_loan = 100000  

    if needs_loan and shortfall > max_loan:
        print(f"     Cannot Build: Shortfall €{shortfall:,.2f} exceeds max loan €{max_loan:,.0f}")
        print(f"     Need budget of at least €{total_cost - max_loan:,.2f} to proceed")
        return total_cost, False  

    print(f"   Needs Loan:    {'  Yes' if needs_loan else '  No'} (shortfall: €{shortfall:,.2f})")
    return total_cost, True  

def get_loan_terms(loan_type):
    terms = {
        "10.000": {"monthly_payment": 333.55, "term_months": 36, "interest_rate": "12%"},
        "50.000": {"monthly_payment": 1050.10, "term_months": 60, "interest_rate": "10%"},
        "100.000": {"monthly_payment": 1534.28, "term_months": 84, "interest_rate": "8%"},
    }
    return terms.get(loan_type)

def handle_loan_process():
    user_choice = input("Choose loan: 10.000 / 50.000 / 100.000: ")
    result = get_loan_terms(user_choice)
    if result:
        print(f"You have to pay €{result['monthly_payment']:,.2f}/month for {result['term_months']} months at {result['interest_rate']}")
    else:
        print("Invalid loan type. Please choose 10.000, 50.000, 100.000")

budget = float(input("What's your budget €? "))

if budget <= 50000:
    print("You can do a renovation or build a small apartment")
    project = input("Do you want to do a renovation or build a small apartment? ")
    
    if project == "renovation":
        sq_meters = float(input("How big of a renovation in square meters? "))
        total_cost, can_build = display_estimate_summary("renovation", sq_meters, budget)
    elif project == "build":
        sq_meters = float(input("How big of a house do you want to build in square meters? "))
        total_cost, can_build = display_estimate_summary("build_small", sq_meters, budget)
    else:
        print("Please, write one of the two.")
        exit()

elif budget <= 160000:
    print("You can build a small house or an apartment")
    project = input("Do you want to build a small house or an apartment? ")
    
    if project == "small house":
        sq_meters = float(input("How big of a house do you want to build in square meters? "))
        total_cost, can_build = display_estimate_summary("house", sq_meters, budget)
    elif project == "apartment":
        sq_meters = float(input("How big of an apartment do you want to build? "))
        total_cost, can_build = display_estimate_summary("apartment", sq_meters, budget)
    else:
        print("Please write one of two.")
        exit()

elif budget <= 1600000:
    print("You can build a villa")
    sq_meters = float(input("How big of a villa do you want? "))
    total_cost, can_build = display_estimate_summary("villa", sq_meters, budget)

else:
    print("You can build a mansion or a skyscraper")
    exit()

if not can_build:
    print("\n  Project not feasible with current budget and loan options.")
elif total_cost > budget:
    loan = input(f"\n   Shortfall: €{total_cost - budget:,.2f}. Do you want a loan? (y/n) ")
    if loan == "n":
        print("Sorry you can't build")
    else:
        handle_loan_process()
else:
    print("\n✅ Project fits within budget. No loan needed.")
