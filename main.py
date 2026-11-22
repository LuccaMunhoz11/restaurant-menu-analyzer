
from input_handling import (
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
    calculate_performance,
    calculate_weekday_period_performance,
    identify_demand_extremes,
    simulate_price_changes
)
from reporting import build_summary_report, price_simulation_report
from generator import generate_orders
from price_simulation import simulate_item_price
from recommendations import generate_menu_recommendations

import argparse
import math


def main():

  # Create the command-line argument parser
  parser = argparse.ArgumentParser(
    description="Restaurant Menu Performance Analyzer"
  )

  # Allow the user to choose the order source (original or generated)
  parser.add_argument(
    "--mode",
    choices=["original", "generated"],
    default="original",
    help="Choose between original and generated orders"
  )

  # Allow the user to choose the number of generated order lines
  parser.add_argument(
    "--num-orders",
    type=int,
    default=500,
    help="Number of synthetic order lines to generate"
  )

  # Allow the user to choose the time-of-day demand profile
  parser.add_argument(
    "--profile",
    choices=["balanced", "lunch_heavy", "dinner_heavy"],
    default="balanced",
    help="Time-of-day demand profile for generated orders"
  )
    
  # Allow the user to control the random seed
  parser.add_argument(
    "--seed",
    type=int,
    default=42,
    help="Random seed for reproducible order generation"
  )

  # Allow the user to choose the starting date of the generated orders
  parser.add_argument(
    "--start-date",
    type=str,
    default="2026-06-01",
    help="Starting date for generated orders (YYYY-MM-DD)"
  )
    
  # Allow the user to choose the number of days covered
  parser.add_argument(
    "--num-days",
    type=int,
    default=30,
    help="Number of consecutive calendar days for generated orders"
  )
  
  #Allow user to simulate a price increase
  parser.add_argument(
    "--price-change",
    type=float,
    default=None,
    help="Hypothetical percentage change applied to all menu prices"
  )


  # Read the arguments provided by the user
  args = parser.parse_args()

  # Validate the requested price change
  if args.price_change is not None:

    if args.price_change < -100:
      parser.error("Price change cannot be below -100%.")

    if not math.isfinite(args.price_change):
      parser.error("Price change must be a finite number.")



    
  print("Restaurant Menu Analyzer")

  # Load and validate the menu
  try:
    menu = load_csv("data/menu.csv", "menu")
  except OSError as error:
    parser.error(f"Cannot read menu file: {error}")
    
  if menu is None:
    parser.error("Menu CSV is empty or missing required columns.")
    
  valid_menu, menu_errors = validate_menu(menu)

  if not valid_menu:
    parser.error("No valid menu items available for analysis.")

  # Branch according to the source of orders (original or generated)
  use_generated_orders = (args.mode == "generated")
    
  if use_generated_orders:
      
    # Attempt to generate synthetic orders
    try:
        orders = generate_orders(
            valid_menu,
            num_orders=args.num_orders,
            profile=args.profile,
            seed=args.seed,
            start_date=args.start_date,
            num_days=args.num_days
        )

    # Handle invalid generator parameters
    except ValueError as error:
        parser.error(str(error))

    orders_source = "results/generated_orders.csv"
      
  else:
      
    try:
        orders = load_csv("data/orders.csv", "orders")
    except OSError as error:
        parser.error(f"Cannot read orders file: {error}")

    if orders is None:
        parser.error("Orders CSV is empty or missing required columns.")

    orders_source = "data/orders.csv"

  # Validate orders (original or generated)
  valid_orders, order_errors = validate_orders(orders, valid_menu)

  if not valid_orders:
    parser.error("No valid order lines available for analysis.")

  # If results doesn't exist, create it
  Path("results").mkdir(exist_ok=True)
    
  # Save synthetic generated orders when the generator is used
  if use_generated_orders:
    save_csv("results/generated_orders.csv", orders)

  # Save validated menu and validated orders
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

  # Generate rule-based recommendations for menu items
  menu_recommendations = generate_menu_recommendations(valid_menu, item_performance)

  # Save menu recommendations to a CSV file
  save_csv("results/menu_recommendations.csv", menu_recommendations) 

  # Perform hypothetical price simulation if requested
  if args.price_change is not None:

    simulated_results = []

    # Apply the same percentage change to every menu item
    for performance in item_performance:
    
      # Search for the corresponding menu item by ID
      for item in valid_menu:
        if item.item_id == performance["item_id"]:
          break
      
      result = simulate_item_price(
        item,
        performance,
        args.price_change
      )

      simulated_results.append(result)
    
    save_csv("results/price_simulation.csv", simulated_results)
  




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

  
  # Calculate combined weekday and time-of-day performance
  weekday_period_performance = calculate_weekday_period_performance(matched_orders)

  # Save the detailed temporal analysis
  save_csv("results/weekday_period_performance.csv", weekday_period_performance)

  
  # Identify busiest and quietest active periods
  busiest, quietest = identify_demand_extremes(weekday_period_performance)  

  # Create plot of menu-wide profit over changes to menu prices by a factor
  simulate_price_changes(valid_menu, item_performance)


  # Generate the consolidated baseline report
  report = build_summary_report(
      menu_file="data/menu.csv",
      orders_file=orders_source,
      valid_menu=valid_menu,
      valid_orders=valid_orders,
      menu_errors=menu_errors,
      order_errors=order_errors,
      item_performance=item_performance,
      category_performance=category_performance,
      ranking_results=ranking_results,
      period_performance=period_performance,
      day_of_week_performance=day_of_week_performance,
      weekday_period_performance=weekday_period_performance,
      busiest=busiest,
      quietest=quietest
  )

  # Add price simulation to report if requested
  if args.price_change is not None:

    report += price_simulation_report(
        simulated_results,
        args.price_change
    )


  # Add generation parameters to the report when synthetic orders are used
  if use_generated_orders:
    report += (
        "\nSYNTHETIC ORDER GENERATION\n"
        f"Profile: {args.profile}\n"
        f"Random seed: {args.seed}\n"
        f"Requested order lines: {args.num_orders}\n"
        f"Start date: {args.start_date}\n"
        f"Number of days: {args.num_days}\n"
    )
    
  # Save and display the structured report
  report_path = Path("results/summary_report.txt")
  report_path.write_text(report, encoding="utf-8")

  print("\n" + report)
  print(f"Report saved: {report_path}")





if __name__ == "__main__":
  main()
