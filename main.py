from restaurant.input_handling import load_csv, validate_menu, validate_orders, save_csv
from pathlib import Path
from analysis import (
    match_orders_to_menu,
    calculate_item_performance,
    calculate_category_performance
)

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

  # Matching the validated orders to the validated menu
  matched_orders = match_orders_to_menu(valid_menu, valid_orders)

  print("Matched order lines:", len(matched_orders))

  # Calculate performance by menu item
  item_performance = calculate_item_performance(valid_menu, matched_orders)

  # Calculate performance by category
  category_performance = calculate_category_performance(item_performance)

  # Save results to CSV files
  save_csv("results/item_performance.csv", item_performance)
  save_csv("results/category_performance.csv", category_performance)

  # Print the results
  print("Item performance calculated:", len(item_performance))
  print("Category performance calculated:", len(category_performance))
  
  for category in category_performance:
      print(
          category["category"],
          "| Units:", category["units_sold"],
          "| Revenue:", category["revenue"],
          "| Cost:", category["estimated_cost"],
          "| Gross Margin:", category["gross_margin"]
      )



if __name__ == "__main__":
  main()
