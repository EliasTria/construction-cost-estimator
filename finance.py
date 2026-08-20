import json

def load_config(path="costs.json"):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "rates": {"renovation_per_sqm": 5.0, "build_small_per_sqm": 5.0,
                      "house_per_sqm": 10.0, "apartment_per_sqm": 10.0, "villa_per_sqm": 20.0},
            "loan_thresholds": {"renovation": 5000, "build_small": 5000,
                                "house": 15000, "apartment": 15000, "villa": 50000}
        }

CONFIG = load_config()

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
        rate = CONFIG["rates"]["renovation_per_sqm"]
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
        rate = CONFIG["rates"]["build_small_per_sqm"]
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
        rate = CONFIG["rates"]["house_per_sqm"]
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
        rate = CONFIG["rates"]["apartment_per_sqm"]
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

    rate = CONFIG["rates"]["villa_per_sqm"]
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
