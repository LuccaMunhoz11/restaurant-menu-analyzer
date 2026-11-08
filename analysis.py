# Function that matches the validated orders to the validated menu, returns the matched orders
def match_orders_to_menu(valid_menu, valid_orders):

    # Create a dictionary to find menu items by item_id
    menu_lookup = {}

    for item in valid_menu:
        menu_lookup[item["item_id"]] = item

    matched_orders = []

    # Match each validated order to its menu item
    for order in valid_orders:
        menu_item = menu_lookup[order["item_id"]]
        matched_order = {
            **order,
            "name": menu_item["name"],
            "category": menu_item["category"],
            "unit_cost": menu_item["unit_cost"],
            "price": menu_item["price"]
        }
        matched_orders.append(matched_order)

    return matched_orders


# Function that calculates the performance of each item, returns a list of item's performance
def calculate_item_performance(valid_menu, matched_orders):

    # Create a dictionary to store each item's results
    item_summary = {}

    # Initialize every menu item, including those with zero sales
    for item in valid_menu:
        item_id = item["item_id"]
        item_summary[item_id] = {
            "item_id": item_id,
            "name": item["name"],
            "category": item["category"],
            "units_sold": 0,
            "revenue": 0.0,
            "estimated_cost": 0.0,
            "gross_margin": 0.0
        }

    # Process each matched order
    for order in matched_orders:
        item_id = order["item_id"]
        quantity = order["quantity"]
        item_summary[item_id]["units_sold"] += quantity
        item_summary[item_id]["revenue"] += (quantity * order["price"])
        item_summary[item_id]["estimated_cost"] += (quantity * order["unit_cost"])

    # Calculate gross margin for every item
    for item in item_summary.values():
        item["revenue"] = round(item["revenue"], 2)
        item["estimated_cost"] = round(item["estimated_cost"], 2)
        item["gross_margin"] = round(item["revenue"] - item["estimated_cost"], 2)

    return list(item_summary.values())


# Function that calculates the performance by category, returns a list of category's performace
def calculate_category_performance(item_performance):

    category_summary = {}

    # Group item results by category
    for item in item_performance:
        category = item["category"]

        # Initialize the category if it doesn't exist
        if category not in category_summary:
            category_summary[category] = {
                "category": category,
                "units_sold": 0,
                "revenue": 0.0,
                "estimated_cost": 0.0,
                "gross_margin": 0.0
            }

        # Accumulate results for the category
        category_summary[category]["units_sold"] += (item["units_sold"])
        category_summary[category]["revenue"] += (item["revenue"])
        category_summary[category]["estimated_cost"] += (item["estimated_cost"])

    # Calculate category margins
    for category in category_summary.values():
        category["revenue"] = round(category["revenue"], 2)
        category["estimated_cost"] = round(category["estimated_cost"], 2)
        category["gross_margin"] = round(category["revenue"] - category["estimated_cost"], 2)

    return list(category_summary.values())


# Function that ranks the menu item's performace, using a ranking criteria and a number "n" (of ranking by top n items, defined initially as top 5)
# Returns best-performing items and worst-performing items
def rank_menu_items(item_performance, criterion, top_n=5):

    # Define the criteria allowed for ranking
    valid_criteria = ["units_sold", "gross_margin"]

    if criterion not in valid_criteria:
        raise ValueError("Invalid ranking criterion.")

    if top_n <= 0:
        raise ValueError("top_n must be positive.")

    # Best-performing items: highest values first
    best_items = sorted(
        item_performance,
        key=lambda item: (-item[criterion], item["item_id"])
    )

    # Worst-performing items: lowest values first
    worst_items = sorted(
        item_performance,
        key=lambda item: (item[criterion], item["item_id"])
    )

    return best_items[:top_n], worst_items[:top_n]

