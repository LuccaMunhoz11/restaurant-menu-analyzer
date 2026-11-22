# Rule-based menu recommendations (E06)


from statistics import median


# Calculate an item's gross margin percentage
def calculate_margin_percentage(item):

    # Avoid division by zero when an item has no selling price
    if item.price == 0:
        return 0.0

    margin_percentage = (
        (item.price - item.unit_cost) / item.price
    ) * 100

    return round(margin_percentage, 2)


# Classify an item using demand and profitability
def classify_menu_item(units_sold, margin_percentage, median_units):

    # Define the profitability threshold
    margin_threshold = 55.0

    # Classify demand and profitability
    low_demand = units_sold == 0 or units_sold < median_units
    low_margin = margin_percentage < margin_threshold

    # Apply the recommendation rules
    if low_demand and not low_margin:
        recommendation = "Promote"
        reason = "Low demand but high profitability."

    elif not low_demand and low_margin:
        recommendation = "Review"
        reason = "High demand but low profitability."

    elif low_demand and low_margin:
        recommendation = "Consider removal"
        reason = "Low demand and low profitability."

    else:
        recommendation = "Maintain"
        reason = "High demand and high profitability."

    return recommendation, reason


# Generate recommendations for every menu item
def generate_menu_recommendations(valid_menu, item_performance):

    # Calculate the median units sold across all menu items
    if not item_performance:
        return []

    median_units = median(
        item["units_sold"] for item in item_performance
    )

    # Create a dictionary to connect performance with menu information
    menu_lookup = {
        item.item_id: item for item in valid_menu
    }

    recommendations = []

    # Evaluate each menu item's performance
    for performance in item_performance:

        menu_item = menu_lookup[performance["item_id"]]

        # Calculate the item's gross margin percentage
        margin_percentage = calculate_margin_percentage(menu_item)

        # Apply the recommendation rules
        recommendation, reason = classify_menu_item(
            performance["units_sold"],
            margin_percentage,
            median_units
        )

        # Store the recommendation and its explanation
        recommendations.append({
            "item_id": performance["item_id"],
            "name": performance["name"],
            "category": performance["category"],
            "units_sold": performance["units_sold"],
            "margin_percentage": margin_percentage,
            "median_units_sold": median_units,
            "recommendation": recommendation,
            "reason": (
                f"{reason} "
                f"Units sold: {performance['units_sold']} "
                f"(menu median: {median_units:g}); "
                f"gross margin: {margin_percentage:.2f}%."
            )
        })

    return recommendations
