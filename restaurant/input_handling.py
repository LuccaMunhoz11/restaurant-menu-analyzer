# The input_handling.py module is responsible for reading the data from menu.csv and orders.csv and
#   verifying if the information is correctly formatted and handle possible errors such as missing files
#   or incorrect values.

from datetime import datetime
import csv

REQUIRED_COLUMNS = {
    "menu": {"item_id", "name", "category", "unit_cost", "price"},
    "orders": {"order_id", "date", "time", "item_id", "quantity"}
}

def load_csv(file_path, file_type):  #menu,orders
    
    # Given a path to a CSV file, its data will be converted in a list of dictionaries
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        # Check if we have column names at all 
        if reader.fieldnames is None:
            print(f"Error: '{file_path}' is empty.")
            return None
        
        
        # Check if the column names are the required column names
        required = REQUIRED_COLUMNS[file_type]
        actual = set(reader.fieldnames)
        missing_columns = required - actual
        
        if missing_columns:
            print(
                f"Error: '{file_path}' is missing columns: "
                f"{', '.join(sorted(missing_columns))}"
            )
            return None



        records = list(reader)

    return records


# Validating data
def validate_menu(menu):

    valid_menu = []     #here we are going to store valid menu items
    errors = []         #here we are going to store invalid menu items
    seen_ids = set()    #since ids must be unique, this will be checked using this set

    # VALIDATING
    for row_number, item in enumerate(menu, start=2):
        
        # row_number refers to the csv row where item is (to localize errors)
        # starts at 2 because first line is designated to the header
        
        # CATEGORIES
        item_id = item.get("item_id", "").strip()
        name = item.get("name", "").strip()
        category = item.get("category", "").strip()

        # Check if these strings are non empty
        if not item_id or not name or not category:
            errors.append(
                f"Row {row_number}: Missing required menu field." # Add to errors
            )
            continue

        # Check for duplicated ids
        if item_id in seen_ids:
            errors.append(
                f"Row {row_number}: Duplicate item_id '{item_id}'." 
            )
            continue

        # NUMERICAL FIELDS
        cost_str = item.get("unit_cost", "").strip()
        price_str = item.get("price", "").strip()

        # Check if they are indeed numerical values
        if not cost_str.replace(".", "", 1).isdigit() or not price_str.replace(".", "", 1).isdigit():
            errors.append(
                f"Row {row_number}: Non numerical cost or price."
            )
            continue

        # Convert strings to floats
        unit_cost = float(cost_str)
        price = float(price_str)

        # Check if the values are in the expected ranges
        if unit_cost < 0 or price < 0:
            errors.append(
                f"Row {row_number}: Invalid cost or price range."
            )
            continue

        #If item reach this point is valid and we store it
        valid_item = item.copy()
        valid_item["unit_cost"] = unit_cost
        valid_item["price"] = price

        valid_menu.append(valid_item)
        seen_ids.add(item_id)

    return valid_menu, errors

def validate_orders(orders, valid_menu):

    valid_orders = []   #here we are going to store valid menu items
    errors = []         #here we are going to store valid menu items

    
    # Orders are made from valid items from menu
    valid_item_ids = set()      

    for item in valid_menu:
        valid_item_ids.add(item["item_id"])



    for row_number, order in enumerate(orders, start=2):
        
        # row_number refers to the csv row where item is (to localize errors)
        # starts at 2 because first line is designated to the header
        
        order_id = order.get("order_id", "").strip()
        date_str = order.get("date", "").strip()
        time_str = order.get("time", "").strip()
        item_id = order.get("item_id", "").strip()
        quantity_str = order.get("quantity", "").strip()

        # Check if all required fields are filled in
        if not order_id or not date_str or not time_str or not item_id or not quantity_str:
            errors.append(
                f"Row {row_number}: Missing required order field."
            )
            continue

        # Check if item exists in the menu
        if item_id not in valid_item_ids:
            errors.append(
                f"Row {row_number}: Unknown item_id '{item_id}'."
            )
            continue

        # Validate quantity format
        if not quantity_str.isdigit(): #Is digit forces our quantity to be an integer
            errors.append(
                f"Row {row_number}: Invalid quantity."
            )
            continue

        quantity = int(quantity_str)

        # Validate quantity range
        if quantity <= 0:
            errors.append(
                f"Row {row_number}: Quantity must be positive."
            )
            continue
        

        # TIME VALIDATION

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"Row {row_number}: Invalid date.")
            continue

        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            errors.append(
                f"Row {row_number}: Invalid time."
            )
            continue


        # Store valid order
        valid_order = order.copy()
        valid_order["quantity"] = quantity

        valid_orders.append(valid_order)

    return valid_orders, errors


#Saving (valid) data
def save_csv(file_path, records):
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())

        writer.writeheader()
        writer.writerows(records)


