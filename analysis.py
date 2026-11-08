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

