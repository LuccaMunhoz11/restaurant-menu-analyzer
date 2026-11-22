# Synthetic order generation (E02)


from datetime import datetime, timedelta
import random


# The generated records must use exactly the same five columns as orders.csv
ORDER_COLUMNS = ("order_id", "date", "time", "item_id", "quantity")

# Each profile defines the relative probability of selecting a service period
PROFILE_WEIGHTS = {
    "balanced": {"Lunch": 1, "Afternoon": 1, "Dinner": 1},
    "lunch_heavy": {"Lunch": 6, "Afternoon": 2, "Dinner": 2},
    "dinner_heavy": {"Lunch": 2, "Afternoon": 2, "Dinner": 6},
}

# Extract the available profile names so the same set is used for validation
TIME_PROFILES = tuple(PROFILE_WEIGHTS)

# Represent each service period as a range of minutes after midnight
# These boundaries match the periods in analysis.classify_time_period():
#   Lunch:     12:00–14:59  -> minute 720 through 899
#   Afternoon: 15:00–18:59  -> minute 900 through 1139
#   Dinner:    19:00–22:59  -> minute 1140 through 1379
SERVICE_PERIODS = {
    "Lunch": (12 * 60, 15 * 60),
    "Afternoon": (15 * 60, 19 * 60),
    "Dinner": (19 * 60, 23 * 60),
}

# Function that validate generator parameters before producing any synthetic orders
def validate_generator_parameters(valid_menu, num_orders, profile, seed, start_date, num_days):

    # There must be at least one valid menu item to select for generated orders
    if not valid_menu:
        raise ValueError("Cannot generate orders from an empty validated menu.")

    # Require a positive whole number of order lines
    if type(num_orders) is not int or num_orders <= 0:
        raise ValueError("num_orders must be a positive integer.")

    # Do not silently use the wrong distribution if a profile is misspelled
    if profile not in TIME_PROFILES:
        raise ValueError(f"profile must be one of: {', '.join(TIME_PROFILES)}.")

    # The random number generator is seeded with an integer for reproducibility
    if type(seed) is not int:
        raise ValueError("seed must be an integer.")

    # num_days defines how many consecutive calendar dates are eligible
    if type(num_days) is not int or num_days <= 0:
        raise ValueError("num_days must be a positive integer.")

    # First verify that the supplied starting date is a real calendar date
    try:
        parsed_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValueError("start_date must be a valid date in YYYY-MM-DD format.") from exc

    # Converting back to text ensures the user supplied EXACTLY YYYY-MM-DD.
    if parsed_date.strftime("%Y-%m-%d") != start_date:
        raise ValueError("start_date must use the exact YYYY-MM-DD format.")

    # Confirm that the last eligible date can be represented by datetime
    # This prevents impossible ranges from failing unexpectedly during generation
    try:
        parsed_date + timedelta(days=num_days - 1)
    except (OverflowError, ValueError) as exc:
        raise ValueError("The generated date range exceeds supported calendar dates.") from exc

# Function that choose a service period by profile, then a random minute in it
def generate_order_time(rng, profile="balanced"):

    if profile not in PROFILE_WEIGHTS:
        raise ValueError(f"profile must be one of: {', '.join(TIME_PROFILES)}.")

    # Retrieve the profile's weights, then draw one integer from 0 up to their total (but not including) 
    # The draw determines the chosen period
    weights = PROFILE_WEIGHTS[profile]
    draw = rng.randrange(sum(weights.values()))
    cumulative_weight = 0

    # Walk through the periods, summing their weights
    # The first period whose cumulative weight exceeds the draw is the selected period
    for period, weight in weights.items():
        cumulative_weight += weight
        if draw < cumulative_weight:
            # Pick any minute within the period, uniformly at random
            # 'last_minute' is excluded, preventing overlap between periods
            first_minute, last_minute = SERVICE_PERIODS[period]
            minute_of_day = rng.randrange(first_minute, last_minute)

            # Convert minutes since midnight into hour and minute components
            hour = minute_of_day // 60
            minute = minute_of_day % 60

            # Format time exactly as HH:MM, compatible with validate_orders()
            return f"{hour:02d}:{minute:02d}"

    # With the current strictly positive profile weights, the loop always returns a time
    # This safeguard makes unexpected modifications obvious
    raise RuntimeError("Unable to select a service period.")


# Return synthetic order lines using the original five-column CSV schema
# The profile controls only the time-of-day distribution
# Each dictionary contains CSV-style strings for validate_orders()
def generate_orders(
    valid_menu,
    num_orders,
    profile="balanced",
    seed=42,
    start_date="2026-06-01",
    num_days=30,
):    

    # Reject unsupported arguments before generating any records
    validate_generator_parameters(
        valid_menu, num_orders, profile, seed, start_date, num_days
    )

    # Use a local RNG instead of random.seed(), which would also change the
    # random state used by other parts of the application
    # A fixed seed produces the same generated orders for the same inputs
    rng = random.Random(seed)

    # Parse the first date only once. Subsequent orders add a random offset
    first_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    # Select only IDs from the validated menu so all item references are valid
    # All menu items have the same selection probability in this version
    item_ids = [item.item_id for item in valid_menu]

    # Store the new order lines as a list of dictionaries
    generated_orders = []

    # Produce exactly num_orders order lines, numbered from 1 to num_orders
    # The term 'order' here means an order line, not a multi-item transaction
    for number in range(1, num_orders + 1):
        # Pick a date in [start_date, start_date + num_days - 1]
        order_date = first_date + timedelta(days=rng.randrange(num_days))

        # Choose the order time according to the requested demand profile
        order_time = generate_order_time(rng, profile)

        # Pick an existing menu item and a positive quantity between 1 and 4
        item_id = rng.choice(item_ids)
        quantity = rng.randint(1, 4)

        # Create one order-line record with the exact CSV field names
        # Identifiers G00001, G00002, ... are unique within this generated file
        # Quantity is a string here because validate_orders() expects raw CSV records and converts valid quantities to integers itself
        generated_orders.append({
            "order_id": f"G{number:05d}",
            "date": order_date.strftime("%Y-%m-%d"),
            "time": order_time,
            "item_id": item_id,
            "quantity": str(quantity),
        })

    # The random date selection can produce lines out of chronological order
    # Sort by date, then time, then ID for predictable, readable CSV output
    generated_orders.sort(key=lambda order: (
        order["date"], order["time"], order["order_id"]
    ))

    # Return records without saving here
    # Exporting them is the responsibility of the existing save_csv() function once integrated into main.py
    return generated_orders
