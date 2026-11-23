# End-to-end command-line tests using temporary input and output folders

import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


# Locate the real entry point without depending on where the test command is run
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_FILE = PROJECT_ROOT / "main.py"


# Check error handling and a complete run of the command-line application
class TestCommandLineIntegration(unittest.TestCase):    

    # Execute main.py in an isolated directory and collect its output
    def run_application(self, working_directory, *arguments):
        
        # Use the same Python interpreter that runs this test suite
        # The working directory controls where main.py looks for data/ and saves results/
        environment = os.environ.copy()
        environment["MPLBACKEND"] = "Agg"  # Save charts without opening a window
        return subprocess.run(
            [sys.executable, str(MAIN_FILE), *arguments],
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=45,
            env=environment,
        )

    # TEST 1
    # A missing menu.csv should produce a clear error, not a traceback
    def test_missing_menu_file_is_reported(self):
        
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self.run_application(temporary_dir)

            # argparse uses exit code 2 for invalid inputs or missing files
            self.assertEqual(result.returncode, 2)
            self.assertIn("Cannot read menu file", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    # TEST 2
    # The program should report a missing orders.csv after loading a valid menu
    def test_missing_orders_file_is_reported(self):
        
        with tempfile.TemporaryDirectory() as temporary_dir:
            data_dir = Path(temporary_dir) / "data"
            data_dir.mkdir()

            # Supply a valid menu but deliberately do not create orders.csv
            (data_dir / "menu.csv").write_text(
                "item_id,name,category,unit_cost,price\n"
                "I001,Pizza,Main,4.00,10.00\n",
                encoding="utf-8",
            )
            result = self.run_application(temporary_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Cannot read orders file", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    # TEST 3
    # Only original and generated are valid --mode selections
    def test_invalid_mode_is_rejected(self):
        
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self.run_application(temporary_dir, "--mode", "invalid")
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid choice", result.stderr)

    # TEST 4
    # A discount below -100% must fail before reading any files
    def test_invalid_price_change_is_rejected(self):
        
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self.run_application(temporary_dir, "--price-change", "-150")
            self.assertEqual(result.returncode, 2)
            self.assertIn("Price change cannot be below -100%", result.stderr)

    # TEST 5
    # A complete original-mode run should calculate and save correct results
    def test_small_dataset_generates_consistent_outputs(self):
        
        with tempfile.TemporaryDirectory() as temporary_dir:
            data_dir = Path(temporary_dir) / "data"
            data_dir.mkdir()

            # Use a controlled menu with one selling item and one unsold item
            (data_dir / "menu.csv").write_text(
                "item_id,name,category,unit_cost,price\n"
                "I001,Pizza,Main,4.00,10.00\n"
                "I002,Soup,Starter,2.00,6.00\n",
                encoding="utf-8",
            )
            # Three pizzas sold in two separate order lines:
            # revenue = 3 * 10 = 30; cost = 3 * 4 = 12; gross margin = 18.
            (data_dir / "orders.csv").write_text(
                "order_id,date,time,item_id,quantity\n"
                "O001,2026-06-01,12:30,I001,2\n"
                "O002,2026-06-01,19:30,I001,1\n",
                encoding="utf-8",
            )

            result = self.run_application(temporary_dir, "--mode", "original")
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            output_dir = Path(temporary_dir) / "results"
            report = output_dir / "summary_report.txt"
            self.assertTrue(report.is_file())
            self.assertIn("Units sold: 3", report.read_text(encoding="utf-8"))
            self.assertIn("Revenue: 30.00 EUR", report.read_text(encoding="utf-8"))
            self.assertIn("Gross margin: 18.00 EUR", report.read_text(encoding="utf-8"))

            # Read the actual exported item records rather than trusting console output
            with (output_dir / "item_performance.csv").open(
                newline="", encoding="utf-8"
            ) as file:
                by_id = {row["item_id"]: row for row in csv.DictReader(file)}

            self.assertEqual(int(by_id["I001"]["units_sold"]), 3)
            self.assertEqual(float(by_id["I001"]["gross_margin"]), 18.0)
            self.assertEqual(int(by_id["I002"]["units_sold"]), 0)

            # Both graphics must be created and contain image data
            for filename in ("dashboard.png", "price_changes.png"):
                self.assertGreater((output_dir / filename).stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
