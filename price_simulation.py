# Hypothetical price-change simulation (E05)

# AUXILIAR FUCTION
# Calculates new price given a percentage_change
def calculate_new_price(original_price, percentage_change):
    
    # A reduction greater than 100% is not allowed
    if percentage_change <= -100:
        raise ValueError("Percentage change cannot be below or equal to -100%.")
    
    new_price = original_price * (1 + percentage_change / 100)
    return round(new_price, 2)


# Simulate revenue and gross margin after a hypothetical price change
def simulate_item_price(item, performance, percentage_change):

    #item gives us the id, name, price
    #performance gives us units_sold, estimated_cost

    # Calculate the hypothetical selling price
    new_price = calculate_new_price( item["price"], percentage_change)

    # Calculate simulated revenue
    simulated_revenue = round(
        performance["units_sold"] * new_price,
    2)

    # Calculate simulated gross margin
    simulated_margin = round(
        simulated_revenue - performance["estimated_cost"],
    2)

    # Retrieve the original financial results
    original_revenue = performance["revenue"]
    original_margin = performance["gross_margin"]

    # Calculate the financial differences
    revenue_change = round(simulated_revenue - original_revenue, 2)
    margin_change = round(simulated_margin - original_margin, 2)
    # These should be equal

    return {
        "item_id": item["item_id"],
        "name": item["name"],
        "original_price": item["price"],
        "simulated_price": new_price,
        "units_sold": performance["units_sold"],
        "original_revenue": original_revenue,
        "simulated_revenue": simulated_revenue,
        "revenue_change": revenue_change,
        "original_gross_margin": original_margin,
        "simulated_gross_margin": simulated_margin,
        "margin_change": margin_change
    }
