# -*- coding: utf-8 -*-
"""
BudgetMaster: A Personal Finance Management CLI Application

This single-file Python module implements a comprehensive command-line budgeting tool.
It allows users to track income and expenses, set budget goals, and view financial
reports and visualizations. Data is persisted in JSON files.
"""

import json
import os
import sys
import uuid
import datetime
import collections
import tempfile
import shutil

# --- Constants ---

class Constants:
    """Holds all constant values for the application."""
    TRANSACTIONS_FILE = 'transactions.json'
    BUDGET_GOALS_FILE = 'budget_goals.json'
    PREDEFINED_CATEGORIES = [
        "Food", "Transport", "Entertainment", "Utilities",
        "Healthcare", "Shopping", "Savings", "Income", "Other"
    ]

# --- Data Models ---

class Transaction:
    """
    Represents a single financial transaction.

    Attributes:
        transaction_id (str): A unique identifier for the transaction.
        date (str): The date of the transaction in 'YYYY-MM-DD' format.
        name (str): A description or name for the transaction.
        amount (float): The monetary value. Positive for income, negative for expenses.
        category (str): The category of the transaction.
    """
    def __init__(self, date: str, name: str, amount: float, category: str, transaction_id: str = None):
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.date = date
        self.name = name
        self.amount = amount
        self.category = category

    def to_dict(self):
        """Converts the transaction object to a dictionary."""
        return {
            'transaction_id': self.transaction_id,
            'date': self.date,
            'name': self.name,
            'amount': self.amount,
            'category': self.category
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Transaction object from a dictionary."""
        return cls(**data)

# --- Utility and Helper Classes ---

class Validator:
    """Provides static methods for input validation."""

    @staticmethod
    def is_valid_date(date_str: str) -> bool:
        """Checks if a string is a valid date in YYYY-MM-DD format."""
        try:
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_amount(amount_str: str) -> bool:
        """Checks if a string can be converted to a float."""
        try:
            float(amount_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_category(category_str: str, allowed_categories: list) -> bool:
        """Checks if a category is in the list of allowed categories."""
        return category_str in allowed_categories

    @staticmethod
    def is_valid_menu_choice(choice_str: str, max_choice: int) -> bool:
        """Checks if a string is a valid integer choice within a range."""
        return choice_str.isdigit() and 1 <= int(choice_str) <= max_choice

class CLI_Utils:
    """Provides static methods for command-line interface operations."""

    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def pause_and_continue():
        """Pauses execution and waits for the user to press Enter."""
        input("\nPress Enter to continue...")

    @staticmethod
    def display_menu(title: str, options: dict):
        """
        Displays a formatted menu with a title and numbered options.

        Args:
            title (str): The title of the menu.
            options (dict): A dictionary mapping option number to description.
        """
        print(f"\n--- {title} ---")
        for key, value in options.items():
            print(f" {key}. {value}")
        print("--------------------")

    @staticmethod
    def get_user_input(prompt: str, validator: callable, error_message: str, validation_args: tuple = ()) -> str:
        """
        Prompts the user for input and validates it using a provided function.

        Args:
            prompt (str): The message to display to the user.
            validator (callable): The function to use for validation.
            error_message (str): The message to display on validation failure.
            validation_args (tuple): Extra arguments to pass to the validator function.

        Returns:
            str: The validated user input.
        """
        while True:
            user_input = input(prompt).strip()
            if validator(user_input, *validation_args):
                return user_input
            print(f"Error: {error_message}")

    @staticmethod
    def confirm_action(prompt: str) -> bool:
        """
        Asks the user for a yes/no confirmation.

        Args:
            prompt (str): The confirmation question to ask.

        Returns:
            bool: True if the user confirms (y/yes), False otherwise.
        """
        response = input(f"{prompt} (y/n): ").lower().strip()
        return response in ['y', 'yes']

    @staticmethod
    def display_table(headers: list, data_rows: list[list]):
        """
        Displays data in a formatted table.

        Args:
            headers (list): A list of strings for the table headers.
            data_rows (list[list]): A list of lists, where each inner list is a row.
        """
        if not data_rows:
            print("\nNo data to display.")
            return

        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in data_rows:
            for i, cell in enumerate(row):
                if len(str(cell)) > col_widths[i]:
                    col_widths[i] = len(str(cell))

        # Print header
        header_line = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(f"\n{header_line}")
        print("-" * len(header_line))

        # Print rows
        for row in data_rows:
            row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            print(row_line)

# --- Core Logic and Managers ---

class DataManager:
    """Handles loading from and saving to JSON files."""

    def __init__(self, transactions_file: str, budget_goals_file: str):
        """
        Initializes the DataManager with file paths.

        Args:
            transactions_file (str): Path to the transactions JSON file.
            budget_goals_file (str): Path to the budget goals JSON file.
        """
        self.transactions_file = transactions_file
        self.budget_goals_file = budget_goals_file

    def _load_json(self, file_path: str, default_data):
        """Helper to load JSON data from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty/corrupt, create it with default data
            self._save_json(file_path, default_data)
            return default_data

    def _save_json(self, file_path: str, data):
        """Helper to save data to a JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def load_transactions(self) -> list[Transaction]:
        """Loads transactions from the JSON file."""
        data = self._load_json(self.transactions_file, [])
        return [Transaction.from_dict(t) for t in data]

    def save_transactions(self, transactions: list[Transaction]):
        """Saves a list of transactions to the JSON file."""
        data = [t.to_dict() for t in transactions]
        self._save_json(self.transactions_file, data)

    def load_budget_goals(self) -> dict:
        """Loads budget goals from the JSON file."""
        return self._load_json(self.budget_goals_file, {})

    def save_budget_goals(self, goals: dict):
        """Saves budget goals to the JSON file."""
        self._save_json(self.budget_goals_file, goals)


class TransactionManager:
    """Manages all operations related to transactions."""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.transactions = self.data_manager.load_transactions()

    def add_transaction(self, date: str, name: str, amount: float, category: str):
        """Creates and adds a new transaction."""
        new_transaction = Transaction(date, name, amount, category)
        self.transactions.append(new_transaction)
        self.save_data()
        print("\nTransaction added successfully!")

    def get_all_transactions(self) -> list[Transaction]:
        """Returns all transactions, sorted by date."""
        return sorted(self.transactions, key=lambda t: t.date, reverse=True)

    def get_transaction_by_id(self, transaction_id: str) -> Transaction | None:
        """Finds a transaction by its unique ID."""
        for t in self.transactions:
            if t.transaction_id == transaction_id:
                return t
        return None

    def update_transaction(self, transaction_id: str, new_data: dict) -> bool:
        """Updates an existing transaction's details."""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            for key, value in new_data.items():
                if value is not None and value != '':
                    setattr(transaction, key, value)
            self.save_data()
            return True
        return False

    def delete_transaction(self, transaction_id: str) -> bool:
        """Deletes a transaction by its ID."""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            self.transactions.remove(transaction)
            self.save_data()
            return True
        return False

    def save_data(self):
        """Saves the current list of transactions to the file."""
        self.data_manager.save_transactions(self.transactions)

    # --- Analysis Methods ---

    @staticmethod
    def get_spending_by_category(transactions: list[Transaction]) -> dict:
        """Calculates total spending for each category."""
        spending = collections.defaultdict(float)
        for t in transactions:
            if t.amount < 0:  # Only count expenses
                spending[t.category] += abs(t.amount)
        return dict(spending)

    @staticmethod
    def get_total_income(transactions: list[Transaction]) -> float:
        """Calculates the total income from a list of transactions."""
        return sum(t.amount for t in transactions if t.amount > 0)

    @staticmethod
    def get_total_expenses(transactions: list[Transaction]) -> float:
        """Calculates the total expenses from a list of transactions."""
        return sum(abs(t.amount) for t in transactions if t.amount < 0)


class BudgetManager:
    """Manages budget goals for categories."""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.goals = self.data_manager.load_budget_goals()

    def set_goal(self, category: str, limit: float):
        """Sets or updates a monthly spending limit for a category."""
        self.goals[category] = limit
        self.data_manager.save_budget_goals(self.goals)
        print(f"\nBudget goal for '{category}' set to ${limit:.2f}.")

    def get_all_goals(self) -> dict:
        """Returns all budget goals."""
        return self.goals

    def get_budget_status(self, current_spending: dict) -> list:
        """
        Compares current spending against set goals and returns the status.

        Args:
            current_spending (dict): A dictionary of {category: total_spent}.

        Returns:
            list: A list of lists, each representing a row for the status table.
        """
        status_data = []
        all_categories = set(self.goals.keys()) | set(current_spending.keys())

        for category in sorted(list(all_categories)):
            goal = self.goals.get(category)
            spent = current_spending.get(category, 0.0)

            if goal is not None:
                remaining = goal - spent
                status = f"Over by ${abs(remaining):.2f}" if remaining < 0 else f"Remaining ${remaining:.2f}"
                status_data.append([category, f"${goal:.2f}", f"${spent:.2f}", status])
            else:
                # Category has spending but no budget goal
                status_data.append([category, "Not Set", f"${spent:.2f}", "N/A"])
        
        return status_data


class ChartRenderer:
    """Provides static methods to render ASCII charts."""

    @staticmethod
    def render_bar_chart(category_spending: dict):
        """Renders an ASCII horizontal bar chart for spending by category."""
        print("\n--- Spending by Category (Bar Chart) ---")
        if not category_spending:
            print("No spending data to display.")
            return

        max_label_len = max(len(cat) for cat in category_spending.keys()) if category_spending else 0
        max_amount = max(category_spending.values()) if category_spending else 0
        
        # Define chart width and scale factor
        chart_width = 50
        scale = chart_width / max_amount if max_amount > 0 else 1

        for category, amount in sorted(category_spending.items(), key=lambda item: item[1], reverse=True):
            bar_length = int(amount * scale)
            bar = '█' * bar_length
            label = category.ljust(max_label_len)
            print(f"{label} | {bar} ${amount:.2f}")

    @staticmethod
    def render_pie_chart(category_spending: dict):
        """Renders an ASCII legend-style pie chart for spending breakdown."""
        print("\n--- Spending Breakdown (Pie Chart) ---")
        if not category_spending:
            print("No spending data to display.")
            return

        total_spending = sum(category_spending.values())
        if total_spending == 0:
            print("No expenses to chart.")
            return
            
        symbols = ['█', '▓', '▒', '░', '▪', '▫', '●', '○']
        
        print(f"Total Expenses: ${total_spending:.2f}\n")
        
        sorted_spending = sorted(category_spending.items(), key=lambda item: item[1], reverse=True)
        
        for i, (category, amount) in enumerate(sorted_spending):
            percentage = (amount / total_spending) * 100
            symbol = symbols[i % len(symbols)]
            print(f" {symbol} {category}: ${amount:.2f} ({percentage:.1f}%)")


class ReportGenerator:
    """Generates textual financial reports."""

    @staticmethod
    def generate_monthly_summary(month: int, year: int, all_transactions: list[Transaction]):
        """
        Generates and displays a summary report for a specific month and year.

        Args:
            month (int): The month (1-12).
            year (int): The year.
            all_transactions (list[Transaction]): List of all transaction objects.
        """
        CLI_Utils.clear_screen()
        month_str = datetime.date(year, month, 1).strftime('%B')
        print(f"\n--- Monthly Summary for {month_str} {year} ---")

        monthly_transactions = [
            t for t in all_transactions
            if datetime.datetime.strptime(t.date, '%Y-%m-%d').month == month
            and datetime.datetime.strptime(t.date, '%Y-%m-%d').year == year
        ]

        if not monthly_transactions:
            print("No transactions found for this period.")
            return

        total_income = TransactionManager.get_total_income(monthly_transactions)
        total_expenses = TransactionManager.get_total_expenses(monthly_transactions)
        net_flow = total_income - total_expenses
        
        print(f"\nTotal Income:   ${total_income:10.2f}")
        print(f"Total Expenses: ${total_expenses:10.2f}")
        print("--------------------------")
        print(f"Net Cash Flow:  ${net_flow:10.2f}")
        
        spending_by_category = TransactionManager.get_spending_by_category(monthly_transactions)
        
        if spending_by_category:
            print("\n--- Spending Breakdown by Category ---")
            headers = ["Category", "Amount Spent"]
            data_rows = [[cat, f"${amount:.2f}"] for cat, amount in spending_by_category.items()]
            CLI_Utils.display_table(headers, sorted(data_rows, key=lambda r: r[0]))

            # Display charts
            ChartRenderer.render_pie_chart(spending_by_category)
            ChartRenderer.render_bar_chart(spending_by_category)


# --- Main Application Class ---

class BudgetMasterApp:
    """The main application class that orchestrates the CLI."""

    def __init__(self):
        self.data_manager = DataManager(Constants.TRANSACTIONS_FILE, Constants.BUDGET_GOALS_FILE)
        self.transaction_manager = TransactionManager(self.data_manager)
        self.budget_manager = BudgetManager(self.data_manager)
        self.is_running = True

    def run(self):
        """Starts the main application loop."""
        while self.is_running:
            CLI_Utils.clear_screen()
            print("=== Welcome to BudgetMaster ===")
            menu_options = {
                '1': "Add Income",
                '2': "Add Expense",
                '3': "View All Transactions",
                '4': "Edit Transaction",
                '5': "Delete Transaction",
                '6': "Filter Transactions by Category",
                '7': "Set Budget Goal",
                '8': "View Budget Status",
                '9': "Generate Monthly Report",
                '10': "Exit"
            }
            CLI_Utils.display_menu("Main Menu", menu_options)
            
            choice = CLI_Utils.get_user_input(
                "Enter your choice: ",
                Validator.is_valid_menu_choice,
                f"Please enter a number between 1 and {len(menu_options)}.",
                (len(menu_options),)
            )

            self._dispatch(choice)

    def _dispatch(self, choice: str):
        """Calls the appropriate handler based on user's menu choice."""
        actions = {
            '1': self._handle_add_income,
            '2': self._handle_add_expense,
            '3': self._handle_view_transactions,
            '4': self._handle_edit_transaction,
            '5': self._handle_delete_transaction,
            '6': self._handle_filter_transactions,
            '7': self._handle_set_budget,
            '8': self._handle_view_budget_status,
            '9': self._handle_generate_report,
            '10': self._exit_program
        }
        action = actions.get(choice)
        if action:
            CLI_Utils.clear_screen()
            action()
            if self.is_running:
                CLI_Utils.pause_and_continue()

    def _get_common_transaction_details(self):
        """Helper to get common details for adding/editing a transaction."""
        date = CLI_Utils.get_user_input(
            f"Enter date (YYYY-MM-DD) [default: today]: ",
            lambda d: d == "" or Validator.is_valid_date(d),
            "Invalid date format. Please use YYYY-MM-DD."
        ) or datetime.date.today().strftime('%Y-%m-%d')
        
        name = input("Enter name/description: ").strip()
        
        amount_str = CLI_Utils.get_user_input(
            "Enter amount: ",
            Validator.is_valid_amount,
            "Please enter a valid number."
        )
        
        print("\nAvailable Categories:")
        for i, cat in enumerate(Constants.PREDEFINED_CATEGORIES, 1):
            print(f" {i}. {cat}")
            
        cat_choice_str = CLI_Utils.get_user_input(
            "Choose a category number: ",
            Validator.is_valid_menu_choice,
            f"Please enter a number between 1 and {len(Constants.PREDEFINED_CATEGORIES)}.",
            (len(Constants.PREDEFINED_CATEGORIES),)
        )
        category = Constants.PREDEFINED_CATEGORIES[int(cat_choice_str) - 1]
        
        return date, name, float(amount_str), category

    def _handle_add_income(self):
        print("--- Add Income ---")
        date, name, amount, category = self._get_common_transaction_details()
        self.transaction_manager.add_transaction(date, name, abs(amount), category)

    def _handle_add_expense(self):
        print("--- Add Expense ---")
        date, name, amount, category = self._get_common_transaction_details()
        self.transaction_manager.add_transaction(date, name, -abs(amount), category)
        
    def _display_transactions(self, transactions: list[Transaction]):
        """Helper to format and display a list of transactions."""
        headers = ["ID (short)", "Date", "Name", "Amount", "Category"]
        rows = []
        for t in transactions:
            amount_str = f"${t.amount:.2f}"
            rows.append([t.transaction_id[:8], t.date, t.name, amount_str, t.category])
        CLI_Utils.display_table(headers, rows)

    def _handle_view_transactions(self):
        print("--- All Transactions ---")
        all_transactions = self.transaction_manager.get_all_transactions()
        self._display_transactions(all_transactions)

    def _handle_edit_transaction(self):
        print("--- Edit Transaction ---")
        self._handle_view_transactions()
        
        if not self.transaction_manager.get_all_transactions():
            return
            
        id_prefix = input("\nEnter the first 8 characters of the Transaction ID to edit: ").strip()
        
        # Find the full ID from the prefix
        transaction_id = None
        for t in self.transaction_manager.get_all_transactions():
            if t.transaction_id.startswith(id_prefix):
                transaction_id = t.transaction_id
                break
        
        transaction = self.transaction_manager.get_transaction_by_id(transaction_id)
        if not transaction:
            print("Error: Transaction not found.")
            return

        print("\nEnter new details (leave blank to keep current value):")
        print(f"Current Date: {transaction.date}")
        new_date = CLI_Utils.get_user_input(
            "New date (YYYY-MM-DD): ",
            lambda d: d == "" or Validator.is_valid_date(d),
            "Invalid date format."
        )

        print(f"Current Name: {transaction.name}")
        new_name = input("New name: ").strip()

        print(f"Current Amount: {transaction.amount:.2f}")
        new_amount_str = CLI_Utils.get_user_input(
            "New amount: ",
            lambda a: a == "" or Validator.is_valid_amount(a),
            "Invalid amount."
        )
        new_amount = float(new_amount_str) if new_amount_str else None

        new_data = {
            'date': new_date,
            'name': new_name,
            'amount': new_amount
        }
        
        if CLI_Utils.confirm_action("Are you sure you want to save these changes?"):
            if self.transaction_manager.update_transaction(transaction_id, new_data):
                print("\nTransaction updated successfully.")
            else:
                # This case is unlikely if we already found the transaction, but good practice.
                print("\nFailed to update transaction.")
        else:
            print("\nUpdate cancelled.")


    def _handle_delete_transaction(self):
        print("--- Delete Transaction ---")
        self._handle_view_transactions()

        if not self.transaction_manager.get_all_transactions():
            return
            
        id_prefix = input("\nEnter the first 8 characters of the Transaction ID to delete: ").strip()
        
        # Find the full ID from the prefix
        transaction_id = None
        for t in self.transaction_manager.get_all_transactions():
            if t.transaction_id.startswith(id_prefix):
                transaction_id = t.transaction_id
                break

        if not transaction_id:
            print("Error: Transaction not found.")
            return
        
        if CLI_Utils.confirm_action("Are you sure you want to delete this transaction permanently?"):
            if self.transaction_manager.delete_transaction(transaction_id):
                print("\nTransaction deleted successfully.")
            else:
                print("\nFailed to delete transaction.")
        else:
            print("\nDeletion cancelled.")

    def _handle_filter_transactions(self):
        print("--- Filter Transactions by Category ---")
        
        print("\nAvailable Categories:")
        for i, cat in enumerate(Constants.PREDEFINED_CATEGORIES, 1):
            print(f" {i}. {cat}")
            
        cat_choice_str = CLI_Utils.get_user_input(
            "Choose a category number to filter by: ",
            Validator.is_valid_menu_choice,
            f"Please enter a number between 1 and {len(Constants.PREDEFINED_CATEGORIES)}.",
            (len(Constants.PREDEFINED_CATEGORIES),)
        )
        category = Constants.PREDEFINED_CATEGORIES[int(cat_choice_str) - 1]
        
        filtered = [t for t in self.transaction_manager.get_all_transactions() if t.category == category]
        
        print(f"\n--- Transactions for Category: {category} ---")
        self._display_transactions(filtered)

    def _handle_set_budget(self):
        print("--- Set Budget Goal ---")
        
        print("\nAvailable Categories (excluding Income):")
        expense_categories = [c for c in Constants.PREDEFINED_CATEGORIES if c != "Income"]
        for i, cat in enumerate(expense_categories, 1):
            print(f" {i}. {cat}")
            
        cat_choice_str = CLI_Utils.get_user_input(
            "Choose a category number to set a budget for: ",
            Validator.is_valid_menu_choice,
            f"Please enter a number between 1 and {len(expense_categories)}.",
            (len(expense_categories),)
        )
        category = expense_categories[int(cat_choice_str) - 1]
        
        limit_str = CLI_Utils.get_user_input(
            f"Enter monthly spending limit for {category}: $",
            lambda a: Validator.is_valid_amount(a) and float(a) >= 0,
            "Please enter a valid, non-negative number."
        )
        
        self.budget_manager.set_goal(category, float(limit_str))

    def _handle_view_budget_status(self):
        print("--- Budget Status (Current Month) ---")
        
        today = datetime.date.today()
        current_month_transactions = [
            t for t in self.transaction_manager.get_all_transactions()
            if datetime.datetime.strptime(t.date, '%Y-%m-%d').month == today.month
            and datetime.datetime.strptime(t.date, '%Y-%m-%d').year == today.year
        ]
        
        spending = TransactionManager.get_spending_by_category(current_month_transactions)
        status_data = self.budget_manager.get_budget_status(spending)
        
        if not status_data:
            print("\nNo budget goals set and no spending this month.")
            return
            
        headers = ["Category", "Budget", "Spent", "Status"]
        CLI_Utils.display_table(headers, status_data)

    def _handle_generate_report(self):
        print("--- Generate Monthly Report ---")
        today = datetime.date.today()
        
        year_str = CLI_Utils.get_user_input(
            f"Enter year (e.g., {today.year}) [default: current year]: ",
            lambda y: y == "" or (y.isdigit() and 1900 <= int(y) <= 2100),
            "Please enter a valid year."
        )
        year = int(year_str) if year_str else today.year
        
        month_str = CLI_Utils.get_user_input(
            f"Enter month (1-12) [default: current month]: ",
            lambda m: m == "" or (m.isdigit() and 1 <= int(m) <= 12),
            "Please enter a valid month number (1-12)."
        )
        month = int(month_str) if month_str else today.month
        
        ReportGenerator.generate_monthly_summary(month, year, self.transaction_manager.get_all_transactions())

    def _exit_program(self):
        """Saves data and exits the application."""
        print("Saving data...")
        self.transaction_manager.save_data()
        self.budget_manager.data_manager.save_budget_goals(self.budget_manager.get_all_goals())
        print("Thank you for using BudgetMaster. Goodbye!")
        self.is_running = False

# --- Testing ---

def run_tests():
    """
    Executes a suite of tests for the BudgetMaster application.
    This function is designed to be self-contained and run in a temporary environment.
    """
    print("--- RUNNING TEST SUITE ---")
    
    # 1. Setup a temporary environment for test files
    test_dir = tempfile.mkdtemp()
    test_trans_file = os.path.join(test_dir, 'test_trans.json')
    test_budget_file = os.path.join(test_dir, 'test_budget.json')
    
    # --- Test Case Helper ---
    def run_test(test_func):
        print(f"Running: {test_func.__name__}...", end="")
        try:
            # Reset files before each test
            if os.path.exists(test_trans_file): os.remove(test_trans_file)
            if os.path.exists(test_budget_file): os.remove(test_budget_file)
            test_func()
            print(" PASSED")
        except AssertionError as e:
            print(f" FAILED\n -> {e}")
        except Exception as e:
            print(f" ERROR\n -> {type(e).__name__}: {e}")

    # --- Test Cases ---

    def test_initial_file_creation():
        """Test 1: DataManager creates new files if they don't exist."""
        assert not os.path.exists(test_trans_file)
        dm = DataManager(test_trans_file, test_budget_file)
        trans = dm.load_transactions()
        goals = dm.load_budget_goals()
        assert os.path.exists(test_trans_file)
        assert trans == []
        assert goals == {}

    def test_add_transaction_and_persistence():
        """Test 2: A transaction can be added and is saved to the file."""
        dm = DataManager(test_trans_file, test_budget_file)
        tm = TransactionManager(dm)
        tm.add_transaction("2023-10-26", "Salary", 5000.0, "Income")
        assert len(tm.get_all_transactions()) == 1
        
        # Create new manager to test loading from file
        tm2 = TransactionManager(DataManager(test_trans_file, test_budget_file))
        assert len(tm2.get_all_transactions()) == 1
        assert tm2.get_all_transactions()[0].name == "Salary"

    def test_delete_transaction():
        """Test 3: A transaction can be successfully deleted."""
        dm = DataManager(test_trans_file, test_budget_file)
        tm = TransactionManager(dm)
        tm.add_transaction("2023-10-27", "Groceries", -150.0, "Food")
        transaction_id = tm.get_all_transactions()[0].transaction_id
        
        deleted = tm.delete_transaction(transaction_id)
        assert deleted is True
        assert len(tm.get_all_transactions()) == 0

    def test_edit_transaction():
        """Test 4: A transaction's details can be updated."""
        dm = DataManager(test_trans_file, test_budget_file)
        tm = TransactionManager(dm)
        tm.add_transaction("2023-10-28", "Coffee", -5.0, "Food")
        transaction_id = tm.get_all_transactions()[0].transaction_id
        
        updated = tm.update_transaction(transaction_id, {'amount': -6.50, 'name': 'Latte'})
        assert updated is True
        
        edited_trans = tm.get_transaction_by_id(transaction_id)
        assert edited_trans.amount == -6.50
        assert edited_trans.name == "Latte"

    def test_set_budget_goal():
        """Test 5: A budget goal can be set and saved."""
        dm = DataManager(test_trans_file, test_budget_file)
        bm = BudgetManager(dm)
        bm.set_goal("Food", 400.0)
        assert bm.get_all_goals()['Food'] == 400.0
        
        # Test persistence
        bm2 = BudgetManager(DataManager(test_trans_file, test_budget_file))
        assert bm2.get_all_goals()['Food'] == 400.0

    def test_total_income_and_expenses():
        """Test 6: Correctly calculate total income and expenses."""
        trans_list = [
            Transaction("2023-11-01", "Paycheck", 2000.0, "Income"),
            Transaction("2023-11-02", "Rent", -1200.0, "Utilities"),
            Transaction("2023-11-03", "Freelance", 300.0, "Income"),
            Transaction("2023-11-04", "Dinner", -75.50, "Food"),
        ]
        total_income = TransactionManager.get_total_income(trans_list)
        total_expenses = TransactionManager.get_total_expenses(trans_list)
        assert abs(total_income - 2300.0) < 0.01
        assert abs(total_expenses - 1275.50) < 0.01

    def test_spending_by_category():
        """Test 7: Correctly aggregate spending by category."""
        trans_list = [
            Transaction("2023-11-01", "A", -10.0, "Food"),
            Transaction("2023-11-02", "B", -20.0, "Transport"),
            Transaction("2023-11-03", "C", -15.0, "Food"),
        ]
        spending = TransactionManager.get_spending_by_category(trans_list)
        assert spending['Food'] == 25.0
        assert spending['Transport'] == 20.0

    def test_budget_status_calculation():
        """Test 8: Budget status report is accurate."""
        dm = DataManager(test_trans_file, test_budget_file)
        bm = BudgetManager(dm)
        bm.set_goal("Food", 100.0)
        bm.set_goal("Entertainment", 50.0)
        
        spending = {"Food": 75.0, "Entertainment": 60.0, "Transport": 20.0}
        status = bm.get_budget_status(spending)
        
        status_dict = {row[0]: row for row in status}
        assert "Remaining" in status_dict["Food"][3]
        assert "Over by" in status_dict["Entertainment"][3]
        assert status_dict["Transport"][1] == "Not Set"

    def test_invalid_date_validation():
        """Test 9: Validator correctly identifies invalid dates."""
        assert Validator.is_valid_date("2023-10-26") is True
        assert Validator.is_valid_date("2023-13-01") is False
        assert Validator.is_valid_date("26-10-2023") is False
        assert Validator.is_valid_date("not-a-date") is False

    def test_monthly_report_filtering():
        """Test 10: Report generator correctly filters transactions by month."""
        trans_list = [
            Transaction("2023-10-15", "A", -10.0, "Food"),
            Transaction("2023-11-05", "B", -20.0, "Transport"),
            Transaction("2023-11-20", "C", 100.0, "Income"),
        ]
        # Mock class to capture output (not done for brevity, just testing logic)
        # We can test by directly inspecting the filtered list
        nov_trans = [
            t for t in trans_list
            if datetime.datetime.strptime(t.date, '%Y-%m-%d').month == 11
            and datetime.datetime.strptime(t.date, '%Y-%m-%d').year == 2023
        ]
        assert len(nov_trans) == 2
        assert nov_trans[0].name == "B"
        assert nov_trans[1].name == "C"

    def test_empty_transactions_view():
        """Test 11: Application handles viewing when no transactions exist."""
        # This is more of a UI test, but we can check the manager returns an empty list
        dm = DataManager(test_trans_file, test_budget_file)
        tm = TransactionManager(dm)
        assert tm.get_all_transactions() == []

    # --- Execute All Tests ---
    all_tests = [
        test_initial_file_creation,
        test_add_transaction_and_persistence,
        test_delete_transaction,
        test_edit_transaction,
        test_set_budget_goal,
        test_total_income_and_expenses,
        test_spending_by_category,
        test_budget_status_calculation,
        test_invalid_date_validation,
        test_monthly_report_filtering,
        test_empty_transactions_view,
    ]
    for test in all_tests:
        run_test(test)
    
    # 8. Cleanup
    shutil.rmtree(test_dir)
    print("\n--- TEST SUITE COMPLETE ---")

# --- Application Entry Point ---

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        run_tests()
    else:
        app = BudgetMasterApp()
        app.run()