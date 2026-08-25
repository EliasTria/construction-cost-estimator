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
        current_index = float(data["value"][-1])
        
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

budget=float(input("Whats your budget €?"))

if (budget) <= 5000:
    print("You can do a renovation or build a small apartment")

    project=input("Do you want to do a renovation or build a small apartment? ")
    if project == "renovation":
        rate = RATES["renovation_per_sqm"]
        threshold = CONFIG["loan_thresholds"]["renovation"]
        renovation_cost = float(input("How big of a renovation in square meters? ")) * rate
        if renovation_cost >= threshold:
            loan=input("Do you want a loan?(y/n)")
            if loan == "n":
                print("Sorry you cant build")
            else:
                handle_loan_process()
        else:
            print("Have a great time")
    elif project == "build":
        rate = RATES["build_small_per_sqm"]
        threshold = CONFIG["loan_thresholds"]["build_small"]
        build_cost = float(input("How big of a house do you want to build in square meters? ")) * rate
        if build_cost >= threshold:
            loan=input("Do you want a loan?(y/n)")
            if loan == "n":
                print("Sorry you cant build")
            else:
                handle_loan_process()
        else:
            print("Have a great time")
    else: print("Please, write one of the two.")

elif (budget) <=15000:
    print("You can build a small house or an apartment")

    project=input("Do you want to build a small house or an apartment? ")
    if project == "small house":
        rate = RATES["house_per_sqm"]
        threshold = CONFIG["loan_thresholds"]["house"]
        house_cost = float(input("How big of a house do you want to build in square meters? ")) * rate
        if house_cost >= threshold:
            loan=input("Do you want a loan?(y/n)")
            if loan == "n":
                print("Sorry you cant build")
            else:
                handle_loan_process()
        else:
            print("Have a great time")
    elif project == "apartment":
        rate = RATES["apartment_per_sqm"]
        threshold = CONFIG["loan_thresholds"]["apartment"]
        apartment_cost=float(input("How big of an apartment do you want to build? ")) * rate
        if apartment_cost >= threshold:
            loan=input("Do you want a loan?(y/n)")
            if loan == "n":
                print("Sorry you cant build")
            else:
                handle_loan_process()
        else:
            print("Have a great time")
elif (budget) <=50000:
    print("You can build a villa")

    rate = RATES["villa_per_sqm"]
    threshold = CONFIG["loan_thresholds"]["villa"]
    villa_cost = float(input("How big of a villa do you want?")) * rate
    if villa_cost >= threshold:
        loan=input("Do you want a loan?(y/n)")
        if loan == "n":
            print("Sorry you cant build")
        else:
            handle_loan_process()
    else:
        print("Have a great time")
else: print("You can build a mansion or a scyscraper")
