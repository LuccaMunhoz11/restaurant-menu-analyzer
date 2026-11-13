# Function to format a category performance table
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

# Function to build a summary report
def build_summary_report(
    menu_file, orders_file,
    valid_menu, valid_orders,
    menu_errors, order_errors,
    item_performance, category_performance,
    ranking_results, period_performance
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

    return "\n".join(lines) + "\n"

