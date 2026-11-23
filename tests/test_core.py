# Automated tests for the Restaurant Orders & Menu Performance Analyzer

# These tests use small controlled examples instead of the complete course datasets
# This makes it easier to verify the expected results and explain any failures

import unittest

# Import the existing project functions that we want to test
# The tests call these functions directly, without running the full main.py program
from analysis import (
    match_orders_to_menu,
    calculate_item_performance,
    rank_menu_items,
)
from generator import generate_orders
from input_handling import validate_menu, validate_orders


# Group the core tests in one class using Python's built-in unittest framework
class TestRestaurantCore(unittest.TestCase):

    # Create a small valid menu before each test that needs it
    def setUp(self):  

        # Define two menu items using the same field names as menu.csv
        # Values are strings because the validation function receives raw CSV-style data
        raw_menu = [
            {"item_id": "I001", "name": "Pizza", "category": "Main",
             "unit_cost": "4.00", "price": "10.00"},
            {"item_id": "I002", "name": "Soup", "category": "Starter",
             "unit_cost": "2.00", "price": "6.00"},
        ]

        # Validate the menu and store the MenuItem objects for the tests
        # setUp() runs before every test, giving each test a fresh menu
        self.menu, errors = validate_menu(raw_menu)

        # The sample menu must be valid; otherwise, the other tests are unreliable
        self.assertEqual(errors, [])

    # TEST 1
    # An order for an unknown item must be rejected clearly
    def test_unknown_item_reference(self):      

        # One order refers to I001 (valid), and another refers to UNKNOWN (invalid)
        orders = [
            {"order_id": "O1", "date": "2026-06-01", "time": "12:30",
             "item_id": "I001", "quantity": "2"},
            {"order_id": "O2", "date": "2026-06-01", "time": "12:45",
             "item_id": "UNKNOWN", "quantity": "1"},
        ]

        # The validation function should keep the valid order and report the bad one
        valid_orders, errors = validate_orders(orders, self.menu)

        # Expect exactly one accepted order and one error message
        self.assertEqual(len(valid_orders), 1)
        self.assertEqual(len(errors), 1)

        # Confirm that the error explains the unknown menu-item reference
        self.assertIn("Unknown item_id", errors[0])

    # TEST 2
    # Check financial formulas and ensure unsold menu items are included
    def test_zero_sales_and_financial_totals(self):
        
        # Sell two pizzas and no soup. This allows us to calculate totals by hand
        orders = [
            {"order_id": "O1", "date": "2026-06-01", "time": "12:30",
             "item_id": "I001", "quantity": "2"},
        ]

        # Validate orders, match them to menu prices/costs, then calculate performance
        valid_orders, errors = validate_orders(orders, self.menu)
        self.assertEqual(errors, [])
        matched = match_orders_to_menu(self.menu, valid_orders)
        performance = calculate_item_performance(self.menu, matched)

        # Use item IDs as dictionary keys to access each item's results easily
        by_id = {item["item_id"]: item for item in performance}

        # Pizza: 2 units; revenue = 2 * 10 = 20 EUR
        # Estimated cost = 2 * 4 = 8 EUR; gross margin = 20 - 8 = 12 EUR
        self.assertEqual(by_id["I001"]["units_sold"], 2)
        self.assertEqual(by_id["I001"]["revenue"], 20.0)
        self.assertEqual(by_id["I001"]["estimated_cost"], 8.0)
        self.assertEqual(by_id["I001"]["gross_margin"], 12.0)

        # Soup has no orders but must still appear with zero units and revenue
        self.assertEqual(by_id["I002"]["units_sold"], 0)
        self.assertEqual(by_id["I002"]["revenue"], 0.0)

    # TEST 3
    # Items with equal results must be ordered consistently by item_id
    def test_ranking_ties_are_deterministic(self):        

        # Both items have equal units sold and gross margin
        # Put I002 first to show that the result is not based on input order
        rows = [
            {"item_id": "I002", "units_sold": 2, "gross_margin": 12.0},
            {"item_id": "I001", "units_sold": 2, "gross_margin": 12.0},
        ]

        # Verify the tie-breaking rule for both supported ranking criteria
        for criterion in ("units_sold", "gross_margin"):
            best, worst = rank_menu_items(rows, criterion, top_n=2)

            # In both directions, tied items must appear in ascending item_id order
            self.assertEqual([r["item_id"] for r in best], ["I001", "I002"])
            self.assertEqual([r["item_id"] for r in worst], ["I001", "I002"])

    # TEST 4
    # Reject invalid monetary values instead of using them in calculations
    def test_invalid_menu_prices_are_rejected(self):        

        # NaN and infinity are accepted by float(), but must not be valid prices/costs
        # A missing price (None) must also produce a controlled validation error
        raw_menu = [
            {"item_id": "X1", "name": "A", "category": "Main",
             "unit_cost": "2", "price": "nan"},
            {"item_id": "X2", "name": "B", "category": "Main",
             "unit_cost": "inf", "price": "5"},
            {"item_id": "X3", "name": "C", "category": "Main",
             "unit_cost": "2", "price": None},
        ]

        # Validate all three invalid records
        valid_menu, errors = validate_menu(raw_menu)

        # None of these items may enter the valid menu, and each must be reported
        self.assertEqual(valid_menu, [])
        self.assertEqual(len(errors), 3)

    # TEST 5
    # A missing order field must generate an error, not crash the program
    def test_missing_order_field_is_rejected(self):     

        # Simulate a CSV order row without a quantity value
        orders = [
            {"order_id": "O1", "date": "2026-06-01", "time": "12:30",
             "item_id": "I001", "quantity": None}
        ]

        # Validate using our small reference menu
        valid_orders, errors = validate_orders(orders, self.menu)

        # Expect no accepted orders and one understandable error message
        self.assertEqual(valid_orders, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required order field", errors[0])

    # TEST 6
    # The same generator settings and random seed must give the same data
    def test_generator_is_reproducible(self):        

        # Generate two independent sets of 20 lines using identical parameters
        first = generate_orders(self.menu, 20, profile="dinner_heavy", seed=42)
        second = generate_orders(self.menu, 20, profile="dinner_heavy", seed=42)

        # A fixed seed must reproduce all generated records in the same order
        self.assertEqual(first, second)

        # Confirm that the generator returns the requested number of order lines
        self.assertEqual(len(first), 20)


# When running this file directly, ask unittest to execute its test methods
# It can also be discovered with: python -m unittest discover -s tests -v
if __name__ == "__main__":
    unittest.main()

