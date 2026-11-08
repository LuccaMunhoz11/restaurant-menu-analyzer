from restaurant.input_handling import load_csv, validate_menu, validate_orders, save_csv
from pathlib import Path
from analysis import match_orders_to_menu

def main():
  print("Restaurant Menu Analyzer")

  # Load data csv's
  menu = load_csv("data/menu.csv", "menu")
  orders = load_csv("data/orders.csv", "orders")

  # Debugging
  valid_menu, menu_errors = validate_menu(menu)
  valid_orders, order_errors = validate_orders(orders, valid_menu)

  print("Valid menu items:", len(valid_menu))
  print("Menu errors:", len(menu_errors))

  print("Valid orders:", len(valid_orders))
  print("Order errors:", len(order_errors))

  Path("results").mkdir(exist_ok=True) # If results doesnt exist create it
  save_csv("results/validated_menu.csv", valid_menu)
  save_csv("results/validated_orders.csv", valid_orders)

  for error in menu_errors + order_errors:
    print(error)

  matched_orders, invalid_references = match_orders_to_menu(menu, orders)

  print("Matched order lines:", len(matched_orders))
  print("Invalid references:", len(invalid_references))
  for invalid in invalid_references:
    print(invalid)


if __name__ == "__main__":
  main()
