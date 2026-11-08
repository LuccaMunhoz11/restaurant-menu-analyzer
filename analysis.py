
def match_orders_to_menu(menu, orders):
    menu_lookup = {}

    for item in menu:
        menu_lookup[item["item_id"]] = item

    matched_orders = []
    invalid_references = []

    for order in orders:
        item_id = order["item_id"]

        if item_id not in menu_lookup:
            invalid_references.append({
                "order_id": order["order_id"],
                "item_id": item_id,
                "reason": "Unknown menu item"
            })
            continue

        menu_item = menu_lookup[item_id]

        matched_order = {
            **order,
            "name": menu_item["name"],
            "category": menu_item["category"],
            "unit_cost": menu_item["unit_cost"],
            "price": menu_item["price"]
        }

        matched_orders.append(matched_order)

    return matched_orders, invalid_references
