from restaurant.input_handling import (
    load_csv, 
    validate_menu, 
    validate_orders, 
    save_csv
)
from pathlib import Path
<<<<<<< Updated upstream
=======
from analysis import (
    match_orders_to_menu,
    calculate_item_performance,
    calculate_category_performance,
    rank_menu_items,
    calculate_period_performance
)

>>>>>>> Stashed changes

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
  
<<<<<<< Updated upstream
=======
  for category in category_performance:
    print(
        category["category"],
        "| Units:", category["units_sold"],
        "| Revenue:", category["revenue"],
        "| Cost:", category["estimated_cost"],
        "| Gross Margin:", category["gross_margin"]
    )

    # Start to rank the results 
    ranking_results = []
    
    # Rank items using the two selected criteria
    for criterion in ["units_sold", "gross_margin"]:
        
        best_items, worst_items = rank_menu_items(item_performance, criterion, top_n=5)
    
        # Display and record best and worst rankings
        for ranking_type, ranked_items in [("Best", best_items), ("Worst", worst_items)]:  
            
            print(f"\n{ranking_type} 5 items by {criterion}:")
    
            for position, item in enumerate(ranked_items, start=1):
                
                value = item[criterion]   
                
                if criterion == "gross_margin":
                    value_display = f"{value:.2f} EUR"
                else:
                    value_display = f"{value} units"   
                    
                print(
                    f"{position}. {item['name']} "
                    f"({item['item_id']}) - {value_display}"
                )
    
                ranking_results.append({
                    "criterion": criterion,
                    "ranking_type": ranking_type,
                    "position": position,
                    "item_id": item["item_id"],
                    "name": item["name"],
                    "units_sold": item["units_sold"],
                    "gross_margin": item["gross_margin"]
                })
    
    # Save all rankings to one CSV file
    save_csv("results/item_rankings.csv", ranking_results)



    # Calculate performance by time period
    period_performance = calculate_period_performance(matched_orders)
    # Save results
    save_csv("results/period_performance.csv", period_performance)
>>>>>>> Stashed changes


if __name__ == "__main__":
  main()
