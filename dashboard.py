# Pandas/Matplotlib Dashboard (E04)

import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import asdict
from pathlib import Path


# Create a graphical dashboard using existing analytical results
def create_dashboard(
    item_performance,
    category_performance,
    day_of_week_performance,
    weekday_period_performance
):

    # Prepare the data using our existing Pandas function
    data = prepare_dashboard_data(
        item_performance,
        category_performance,
        day_of_week_performance,
        weekday_period_performance
    )

    # Create a figure with four spaces for our graphs
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Define the dashboard title
    fig.suptitle(
        "Restaurant Menu Performance Dashboard",
        fontsize=16,
        fontweight="bold"
    )

    # GRAPH 1 - GROSS MARGIN BY CATEGORY

    # Retrieve category performance, reversing the order
    # so the most profitable category appears at the top
    category_df = data["categories"].iloc[::-1]

    # Select the first graph position (top-left)
    ax = axes[0, 0]

    # Create a horizontal bar chart
    ax.barh(
        category_df["category"],
        category_df["gross_margin"],
        color="steelblue"
    )

    # Add labels and title
    ax.set_title("Gross Margin by Category")
    ax.set_xlabel("Gross Margin (EUR)")
    ax.set_ylabel("Category")

    # Add a grid to make values easier to compare
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)

    
    # GRAPH 2 - TOP 5 BEST-SELLING MENU ITEMS

    # Retrieve the five best-selling items
    top_items_df = data["top_items"].iloc[::-1]

    # Select the second graph position (top-right)
    ax = axes[0, 1]

    # Create a horizontal bar chart
    ax.barh(
        top_items_df["name"],
        top_items_df["units_sold"],
        color="darkorange"
    )

    # Add labels and title
    ax.set_title("Top 5 Best-Selling Menu Items")
    ax.set_xlabel("Units Sold")
    ax.set_ylabel("Menu Item")

    # Add a grid to make comparisons easier
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)

    
    # GRAPH 3 - DEMAND BY DAY OF THE WEEK

    # Retrieve weekday performance
    weekday_df = data["weekdays"]

    # Select the third graph position (bottom-left)
    ax = axes[1, 0]

    # Create a vertical bar chart
    ax.bar(
        weekday_df.index,
        weekday_df["items_sold"],
        color="seagreen"
    )

    # Add labels and title
    ax.set_title("Demand by Day of the Week")
    ax.set_xlabel("Day of the Week")
    ax.set_ylabel("Units Sold")

    # Rotate weekday labels to improve readability
    plt.setp(
        ax.get_xticklabels(),
        rotation=35,
        ha="right"
    )

    # Add a grid to make comparisons easier
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)
  
    
    # GRAPH 4 - DEMAND HEATMAP BY WEEKDAY AND TIME PERIOD

    # Retrieve the prepared heatmap DataFrame
    heatmap_df = data["heatmap"]

    # Select the fourth graph position (bottom-right)
    ax = axes[1, 1]

    # Create the heatmap
    heatmap = ax.imshow(
        heatmap_df.to_numpy(),
        cmap="YlGnBu",
        aspect="auto"
    )

    # Add the chart title
    ax.set_title("Demand by Weekday and Time Period")

    # Define the axis labels
    ax.set_xticks(range(len(heatmap_df.columns)))
    ax.set_xticklabels(heatmap_df.columns)

    ax.set_yticks(range(len(heatmap_df.index)))
    ax.set_yticklabels(heatmap_df.index)

    ax.set_xlabel("Time of Day")
    ax.set_ylabel("Day of the Week")

    # Rotate the time-period labels
    plt.setp(
        ax.get_xticklabels(),
        rotation=35,
        ha="right"
    )

    # Add a color scale representing units sold
    colorbar = fig.colorbar(
        heatmap,
        ax=ax
    )

    colorbar.set_label("Units Sold")
    
    # Display the number of units sold inside each cell
    max_units = heatmap_df.to_numpy().max()

    for day_index in range(len(heatmap_df.index)):

        for period_index in range(len(heatmap_df.columns)):

            # Retrieve the number of units sold
            units = heatmap_df.iloc[
                day_index, period_index
            ]

            # Choose readable text color
            text_color = (
                "white"
                if max_units > 0 and units > max_units / 2
                else "black"
            )

            # Add the value inside the corresponding cell
            ax.text(
                period_index,
                day_index,
                f"{units:d}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9
            )


    # Adjust spacing between dashboard elements
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    # Save the dashboard as an image
    output_path = Path("results/dashboard.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight"
    )

    # Close the figure to release memory
    plt.close(fig)

    return output_path



# Prepare the existing analytical results for visualization
def prepare_dashboard_data(
    item_performance,
    category_performance,
    day_of_week_performance,
    weekday_period_performance
):

    # Convert the results into Pandas DataFrames
    item_df = pd.DataFrame(item_performance)

    category_df = pd.DataFrame(category_performance)

    weekday_df = pd.DataFrame([
        asdict(day) for day in day_of_week_performance
    ])

    weekday_period_df = pd.DataFrame(weekday_period_performance)

    # Identify the five best-selling menu items
    top_items_df = item_df.sort_values(
        by=["units_sold", "item_id"],
        ascending=[False, True]
    ).head(5)

    # Sort categories by gross margin
    category_df = category_df.sort_values(
        by=["gross_margin", "category"],
        ascending=[False, True]
    )

    # Define the correct weekday and time-period order
    weekdays = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    periods = [
        "Morning", "Lunch", "Afternoon",
        "Dinner", "Late night"
    ]

    # Arrange weekday demand chronologically
    weekday_df = weekday_df.set_index(
        "period"
    ).reindex(weekdays)

    # Create a table combining weekdays and time periods
    heatmap_df = weekday_period_df.pivot(
        index="day",
        columns="period",
        values="units_sold"
    )

    heatmap_df = heatmap_df.reindex(
        index=weekdays,
        columns=periods
    ).fillna(0).astype(int)

    # Calculate overall indicators from existing results
    totals = {
        "units_sold": int(item_df["units_sold"].sum()),
        "revenue": round(item_df["revenue"].sum(), 2),
        "gross_margin": round(
            item_df["gross_margin"].sum(), 2
        )
    }

    # Return the prepared data for visualization
    return {
        "top_items": top_items_df,
        "categories": category_df,
        "weekdays": weekday_df,
        "heatmap": heatmap_df,
        "totals": totals
    }


