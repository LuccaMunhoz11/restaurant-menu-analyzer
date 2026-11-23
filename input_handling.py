# The input_handling.py module is responsible for reading the data from menu.csv and orders.csv and
#   verifying if the information is correctly formatted and handle possible errors such as missing files
#   or incorrect values.

import dataclasses
from datetime import datetime
import csv
from typing import List, Tuple

from menu_item import MenuItem

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
def validate_menu(menu) -> Tuple[List[MenuItem], List[str]]:

    valid_menu: List[MenuItem] = []     #here we are going to store valid menu items
    errors = []         #here we are going to store invalid menu items
    seen_ids = set()    #since ids must be unique, this will be checked using this set

    # VALIDATING
    for row_number, item in enumerate(menu, start=2):
        
        # row_number refers to the csv row where item is (to localize errors)
        # starts at 2 because first line is designated to the header
        
        mu = MenuItem()
        # CATEGORIES
        # Retrieve menu fields, safely handling missing values
        mu.item_id = (item.get("item_id") or "").strip()
        mu.name = (item.get("name") or "").strip()
        mu.category = (item.get("category") or "").strip()
        cost_str = (item.get("unit_cost") or "").strip()
        price_str = (item.get("price") or "").strip()

        try:
            mu.validate_categories()
            mu.validate_numerical_fields(cost_str, price_str)
        except ValueError as e:
            errors.append(f"Row {row_number}: {e}")
            continue

        # Check for duplicated menu item IDs
        if mu.item_id in seen_ids:
            errors.append(
                f"Row {row_number}: Duplicate item_id '{mu.item_id}'."
            )
            continue
        
        valid_menu.append(mu)
        seen_ids.add(mu.item_id)

    return valid_menu, errors

def validate_orders(orders, valid_menu):

    valid_orders = []   #here we are going to store valid menu items
    errors = []         #here we are going to store valid menu items

    
    # Orders are made from valid items from menu
    valid_item_ids = set()      

    for item in valid_menu:
        valid_item_ids.add(item.item_id)



    for row_number, order in enumerate(orders, start=2):
        
        # row_number refers to the csv row where item is (to localize errors)
        # starts at 2 because first line is designated to the header
        
        # Retrieve order fields, safely handling missing values
        order_id = (order.get("order_id") or "").strip()
        date_str = (order.get("date") or "").strip()
        time_str = (order.get("time") or "").strip()
        item_id = (order.get("item_id") or "").strip()
        quantity_str = (order.get("quantity") or "").strip()

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

        if type(records[0]) == dict:
            fieldnames = records[0].keys()
        else:
            fieldnames = [field.name for field in dataclasses.fields(type(records[0]))]
            records = [dataclasses.asdict(r) for r in records]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(records)


