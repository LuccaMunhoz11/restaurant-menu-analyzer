from recommendations import MARGIN_THRESHOLD


# Format category performance table
def format_category_table(category_performance):
    header = (
        f"{'Category':<12} {'Units':>8} {'Revenue EUR':>14} "
        f"{'Cost EUR':>12} {'Margin EUR':>12}"
    )

    lines = [header, "-" * len(header)]

    for category in sorted(
        category_performance,
        key=lambda row: row["category"]
    ):
        lines.append(
            f"{category['category']:<12} "
            f"{category['units_sold']:>8} "
            f"{category['revenue']:>14.2f} "
            f"{category['estimated_cost']:>12.2f} "
            f"{category['gross_margin']:>12.2f}"
        )

    return "\n".join(lines)

# Build a summary report
def build_summary_report(
    menu_file, orders_file,
    valid_menu, valid_orders,
    menu_errors, order_errors,
    item_performance, category_performance,
    ranking_results, period_performance,
    day_of_week_performance,
    weekday_period_performance,
    busiest, quietest
):
    # Overall financial indicators
    total_units = sum(
        item["units_sold"] for item in item_performance
    )
    total_revenue = sum(
        item["revenue"] for item in item_performance
    )
    total_cost = sum(
        item["estimated_cost"] for item in item_performance
    )

    total_margin = total_revenue - total_cost
    margin_percentage = (
        100 * total_margin / total_revenue
        if total_revenue else 0.0
    )

    dates = [order["date"] for order in valid_orders]
    date_range = (
        f"{min(dates)} to {max(dates)}"
        if dates else "No valid orders"
    )

    lines = [
        "RESTAURANT MENU PERFORMANCE - BASELINE REPORT",
        "=" * 48,
        f"Menu input: {menu_file}",
        f"Orders input: {orders_file}",
        f"Period: {date_range}",
        f"Valid menu items: {len(valid_menu)}",
        f"Invalid menu records: {len(menu_errors)}",
        f"Valid order lines: {len(valid_orders)}",
        f"Invalid order lines: {len(order_errors)}",
        "",
        "OVERALL SALES",
        f"Units sold: {total_units}",
        f"Revenue: {total_revenue:.2f} EUR",
        f"Estimated cost: {total_cost:.2f} EUR",
        f"Gross margin: {total_margin:.2f} EUR",
        f"Gross margin rate: {margin_percentage:.2f}%",
        "",
        "PERFORMANCE BY CATEGORY",
        format_category_table(category_performance),
        "",
        "ITEM RANKINGS",
    ]

    # Include existing best/worst rankings
    for criterion in ("units_sold", "gross_margin"):
        for ranking_type in ("Best", "Worst"):
            lines.append(
                f"{ranking_type} 5 by {criterion}:"
            )

            matching = [
                row for row in ranking_results
                if row["criterion"] == criterion
                and row["ranking_type"] == ranking_type
            ]

            for row in sorted(
                matching, key=lambda x: x["position"]
            ):
                if criterion == "units_sold":
                    value = f"{row['units_sold']} units"
                else:
                    value = f"{row['gross_margin']:.2f} EUR"

                lines.append(
                    f"  {row['position']}. {row['name']} "
                    f"({row['item_id']}): {value}"
                )

            lines.append("")

    # Existing basic time-of-day analysis
    lines += [
        "DEMAND BY TIME OF DAY",
        f"{'Period':<12} {'Order lines':>12} "
        f"{'Units':>8} {'Revenue EUR':>14} "
        f"{'Demand %':>10}",
    ]

    for period in period_performance:
        lines.append(
            f"{period.period:<12} "
            f"{period.orders:>12} "
            f"{period.items_sold:>8} "
            f"{period.revenue:>14.2f} "
            f"{period.demand:>10.2f}"
        )
        
    # Detailed demand analysis by weekday
    lines += [
        "",
        "DEMAND BY DAY OF WEEK",
        f"{'Day':<12} {'Order lines':>12} "
        f"{'Units':>8} {'Revenue EUR':>14} "
        f"{'Demand %':>10}",
    ]

    for day in day_of_week_performance:
        lines.append(
            f"{day.period:<12} "
            f"{day.orders:>12} "
            f"{day.items_sold:>8} "
            f"{day.revenue:>14.2f} "
            f"{day.demand:>10.2f}"
        )
    
    # Detailed weekday and time-of-day performance
    lines += [
        "",
        "DETAILED DEMAND BY WEEKDAY AND TIME PERIOD",
        f"{'Day':<12} {'Period':<12} {'Order lines':>12} "
        f"{'Units':>8} {'Revenue EUR':>14}",
    ]

    for result in weekday_period_performance:
        lines.append(
            f"{result['day']:<12} "
            f"{result['period']:<12} "
            f"{result['order_lines']:>12} "
            f"{result['units_sold']:>8} "
            f"{result['revenue']:>14.2f}"
        )

    # Summary of demand extremes
    lines += [
        "",
        "DEMAND EXTREMES",
    ]

    if busiest is not None:
        lines.append(
            f"Busiest period: {busiest['day']} {busiest['period']} "
            f"({busiest['units_sold']} units sold)"
        )

        lines.append(
            f"Quietest active period: {quietest['day']} "
            f"{quietest['period']} "
            f"({quietest['units_sold']} units sold)"
        )

    else:
        lines.append("No active periods available.")

    
    return "\n".join(lines) + "\n"

# Format hypothetical price simulation results
def price_simulation_report(simulated_results, percentage_change):

    lines = [
        "",
        "HYPOTHETICAL PRICE SIMULATION",
        "=" * 48,
        f"Applied price change: {percentage_change:+.2f}%",
        ""
    ]

    # Calculate overall financial results
    original_revenue = sum(
        item["original_revenue"] for item in simulated_results
    )

    simulated_revenue = sum(
        item["simulated_revenue"] for item in simulated_results
    )

    original_margin = sum(
        item["original_gross_margin"] for item in simulated_results
    )

    simulated_margin = sum(
        item["simulated_gross_margin"] for item in simulated_results
    )

    # Add overall comparison to the report
    lines += [
        f"Original revenue: {original_revenue:.2f} EUR",
        f"Simulated revenue: {simulated_revenue:.2f} EUR",
        f"Revenue difference: {simulated_revenue - original_revenue:+.2f} EUR",
        "",
        f"Original gross margin: {original_margin:.2f} EUR",
        f"Simulated gross margin: {simulated_margin:.2f} EUR",
        f"Margin difference: {simulated_margin - original_margin:+.2f} EUR"
    ]

    return "\n".join(lines) + "\n"


# Format the rule-based menu recommendations
def menu_recommendations_report(menu_recommendations):

    lines = [
        "",
        "RULE-BASED MENU RECOMMENDATIONS",
        "=" * 48,
    ]

    if not menu_recommendations:
        lines.append("No menu recommendations available.")
        return "\n".join(lines) + "\n"

    # Retrieve the demand threshold used by the recommendation engine
    median_units = menu_recommendations[0]["median_units_sold"]

    lines += [
        f"Demand threshold (median units): {median_units:g}",
        f"Gross margin threshold: {MARGIN_THRESHOLD:.2f}%",
        "Values at or above the thresholds are classified as high.",
        "",
        "RECOMMENDATION SUMMARY",
    ]

    # Define the recommendation categories
    categories = [
        "Promote",
        "Review",
        "Consider removal",
        "Maintain"
    ]

    # Group menu items by their recommendation
    grouped = {category: [] for category in categories}

    for item in menu_recommendations:
        grouped[item["recommendation"]].append(item)

    # Count the items in each recommendation category
    for category in categories:
        lines.append(
            f"{category}: {len(grouped[category])} items"
        )

    # Show a few examples without overcrowding the report
    lines += [
        "",
        "RECOMMENDATION EXAMPLES",
        "(First 2 items in menu order per category)"
    ]

    for category in categories:

        if not grouped[category]:
            continue

        lines.append(f"\n{category}:")

        for item in grouped[category][:2]:
            lines.append(
                f"  {item['name']} ({item['item_id']}): "
                f"{item['reason']}"
            )

    lines += [
        "",
        "Full recommendations: results/menu_recommendations.csv"
    ]

    return "\n".join(lines) + "\n"
