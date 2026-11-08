# Function that matches the validated orders to the validated menu
# Returns the matched orders
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

# Function that calculates the performance of each item
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

