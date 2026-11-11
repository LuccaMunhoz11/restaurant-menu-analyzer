from restaurant.input_handling import (
    load_csv, 
    validate_menu, 
    validate_orders, 
    save_csv
)
from pathlib import Path
from analysis import (
    match_orders_to_menu,
    calculate_item_performance,
    calculate_category_performance,
    rank_menu_items,
    calculate_performance
)
from reporting import build_summary_report


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
    
  # Start to rank the results 
  ranking_results = []
    
  # Rank items using the two selected criteria
  for criterion in ["units_sold", "gross_margin"]:
        
      best_items, worst_items = rank_menu_items(item_performance, criterion, top_n=5)
    
      # Display and record best and worst rankings
      for ranking_type, ranked_items in [("Best", best_items), ("Worst", worst_items)]:                  
        
            for position, item in enumerate(ranked_items, start=1):                                            
                
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
  period_performance, day_of_week_performance = calculate_performance(matched_orders)
    
  # Save results of performace
  save_csv("results/period_performance.csv", period_performance)
  save_csv("results/day_of_week_performance.csv", day_of_week_performance)

  # Generate the consolidated baseline report
  report = build_summary_report(
      menu_file="data/menu.csv",
      orders_file="data/orders.csv",
      valid_menu=valid_menu,
      valid_orders=valid_orders,
      menu_errors=menu_errors,
      order_errors=order_errors,
      item_performance=item_performance,
      category_performance=category_performance,
      ranking_results=ranking_results,
      period_performance=period_performance
  )

  # Save and display the structured report
  report_path = Path("results/summary_report.txt")
  report_path.write_text(report, encoding="utf-8")

  print("\n" + report)
  print(f"Report saved: {report_path}")





if __name__ == "__main__":
  main()
