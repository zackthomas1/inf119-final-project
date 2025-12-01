# -*- coding: utf-8 -*-
"""
BudgetMaster: A self-contained command-line budgeting application.

This module provides a complete solution for personal finance management,
including transaction tracking, budget setting, reporting, and data visualization,
all within a single Python file.
"""

import json
import os
import sys
from datetime import datetime
import math
from collections import defaultdict

# --- Constants ---
TRANSACTIONS_FILE = 'transactions.json'
BUDGET_GOALS_FILE = 'budget_goals.json'
PREDEFINED_CATEGORIES = [
    "Food", "Transport", "Entertainment", "Utilities",
    "Healthcare", "Shopping", "Savings", "Income"
]


class DataManager:
    """Handles data persistence, loading from and saving to JSON files."""

    def __init__(self, transactions_path, budget_goals_path):
        """
        Initializes the DataManager with paths to data files.

        Args:
            transactions_path (str): The file path for transactions.
            budget_goals_path (str): The file path for budget goals.
        """
        self.transactions_path = transactions_path
        self.budget_goals_path = budget_goals_path
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Creates data files with default empty content if they don't exist."""
        for path in [self.transactions_path, self.budget_goals_path]:
            if not os.path.exists(path):
                # Both transaction and budget files store a list of objects.
                default_content = []
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f)
                # Quietly create files to avoid cluttering test output
                # print(f"Info: Created missing data file at '{path}'.")

    def load_data(self, filepath, default_factory=list):
        """
        Loads data from a JSON file.

        Args:
            filepath (str): The path to the JSON file.
            default_factory (callable): A function to call to get default data.

        Returns:
            The data loaded from the file, or a default value on error.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Warning: Could not read or decode {filepath}. Starting with empty data.")
            return default_factory()

    def save_data(self, filepath, data):
        """
        Saves data to a JSON file.

        Args:
            filepath (str): The path to the JSON file.
            data (list or dict): The data to save.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error: Could not save data to {filepath}. Reason: {e}")

    def load_transactions(self):
        """Loads all transactions from the transactions file."""
        return self.load_data(self.transactions_path, default_factory=list)

    def save_transactions(self, transactions):
        """Saves all transactions to the transactions file."""
        self.save_data(self.transactions_path, transactions)

    def load_budget_goals(self):
        """Loads all budget goals from the budget goals file."""
        goals_list = self.load_data(self.budget_goals_path, default_factory=list)
        if not isinstance(goals_list, list):
            print(f"Warning: Data in {self.budget_goals_path} is not a list. Starting with empty goals.")
            return {}
        # Budget goals are stored as a list of dicts, but used as a dict internally for quick lookups.
        return {goal.get('category'): goal.get('limit') for goal in goals_list if isinstance(goal, dict)}


    def save_budget_goals(self, goals_data):
        """Saves all budget goals to the budget goals file."""
        # The app uses a dictionary for goals, which must be converted to a list of dicts for JSON storage.
        # This also handles test fixtures passing a list directly.
        goals_list = []
        if isinstance(goals_data, dict):
            goals_list = [{'category': c, 'limit': l} for c, l in goals_data.items()]
        elif isinstance(goals_data, list):
            # Assume list is already in the correct format for saving.
            goals_list = goals_data
        
        self.save_data(self.budget_goals_path, goals_list)


class UI:
    """A collection of static methods for handling user interface interactions."""

    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def display_header(title):
        """Displays a formatted header."""
        print("\n" + "=" * 40)
        print(f" {title.upper()} ".center(40, "="))
        print("=" * 40)

    @staticmethod
    def display_menu(options):
        """
        Displays a numbered menu of options.

        Args:
            options (dict): A dictionary where keys are descriptions and values are functions.
        """
        print("\nPlease select an option:")
        for i, option in enumerate(options.keys(), 1):
            print(f" {i}. {option}")

    @staticmethod
    def get_validated_input(prompt, validator, error_message):
        """
        Prompts the user for input and validates it using a provided function.

        Args:
            prompt (str): The message to display to the user.
            validator (function): A function that takes the input and returns a valid value or raises a ValueError.
            error_message (str): The message to display if validation fails.

        Returns:
            The validated and processed user input.
        """
        while True:
            try:
                user_input = input(prompt)
                return validator(user_input)
            except ValueError as e:
                # Use the validator's specific error if available
                specific_error = str(e) if str(e) else error_message
                print(f"Error: {specific_error}. Please try again.")

    @staticmethod
    def get_confirmation(prompt):
        """
        Gets a yes/no confirmation from the user.

        Args:
            prompt (str): The confirmation question to ask.

        Returns:
            bool: True if the user confirms (yes), False otherwise.
        """
        response = input(f"{prompt} (y/n): ").lower().strip()
        return response in ['y', 'yes']

    @staticmethod
    def print_message(message, msg_type='info'):
        """Prints a formatted message."""
        prefix = f"{msg_type.upper()}:"
        print(f"{prefix} {message}")

    @staticmethod
    def print_table(headers, data):
        """
        Prints data in a formatted table.

        Args:
            headers (list): A list of strings for the table header.
            data (list of dicts): A list of dictionaries, where each dict is a row.
        """
        if not data:
            print("No data to display.")
            return

        # Calculate column widths
        col_widths = {key: len(key) for key in headers}
        for row in data:
            for key, value in row.items():
                if key in col_widths:
                    col_widths[key] = max(col_widths[key], len(str(value)))

        # Print header
        header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
        print(header_line)
        print("-" * len(header_line))

        # Print rows
        for row in data:
            row_line = " | ".join(str(row.get(header, '')).ljust(col_widths[header]) for header in headers)
            print(row_line)

    @staticmethod
    def press_enter_to_continue():
        """Pauses execution until the user presses Enter in an interactive session."""
        if sys.stdout.isatty():
            input("\nPress Enter to continue...")

# --- Input Validators ---
def validate_date(date_str):
    """Validator for YYYY-MM-DD date format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return date_str
    except ValueError:
        raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

def validate_not_empty(text):
    """Validator to ensure input is not empty."""
    if not text.strip():
        raise ValueError("Input cannot be empty.")
    return text.strip()

def validate_amount(amount_str, allow_negative=True):
    """Validator for numeric amounts."""
    try:
        amount = float(amount_str)
    except (ValueError, TypeError):
        raise ValueError("Invalid number. Please enter a valid amount.")
    
    if not allow_negative and amount < 0:
        raise ValueError("Amount cannot be negative.")
    return amount

def validate_category(category_str, all_categories):
    """Validator to ensure category is valid or new."""
    category = category_str.strip().title()
    if not category:
        raise ValueError("Category cannot be empty.")
    # No strict validation against the list; allows new categories to be added.
    return category


class BudgetMasterApp:
    """The main application class for BudgetMaster."""

    def __init__(self):
        """Initializes the application, loads data, and sets up the menu."""
        self.data_manager = DataManager(TRANSACTIONS_FILE, BUDGET_GOALS_FILE)
        self.transactions = self.data_manager.load_transactions()
        self.budget_goals = self.data_manager.load_budget_goals()
        self.running = True
        self.menu_options = {
            "Add Income": self._add_income,
            "Add Expense": self._add_expense,
            "View All Transactions": self._view_transactions_menu,
            "Edit Transaction": self._edit_transaction,
            "Delete Transaction": self._delete_transaction,
            "Filter Transactions": self._filter_transactions_menu,
            "Set Budget Goal": self._set_budget_goal,
            "View Budget Status": self._view_budget_status,
            "Generate Monthly Summary Report": self._generate_monthly_summary,
            "View Spending Pie Chart": self._generate_pie_chart,
            "View Spending Bar Chart": self._generate_bar_chart,
            "Exit": self._exit_app
        }

    def run(self):
        """Starts and runs the main application loop."""
        while self.running:
            UI.clear_screen()
            UI.display_header("BudgetMaster Main Menu")
            UI.display_menu(self.menu_options)
            
            choice_str = input("\nEnter your choice: ")
            try:
                choice_index = int(choice_str) - 1
                if 0 <= choice_index < len(self.menu_options):
                    # Get the function from the ordered list of keys
                    menu_function = list(self.menu_options.values())[choice_index]
                    menu_function()
                else:
                    UI.print_message("Invalid choice, please select a number from the menu.", "error")
                    UI.press_enter_to_continue()
            except ValueError:
                UI.print_message("Invalid input. Please enter a number.", "error")
                UI.press_enter_to_continue()

    def _get_next_transaction_id(self):
        """Generates a new unique ID for a transaction."""
        if not self.transactions:
            return 1
        return max(t.get('id', 0) for t in self.transactions) + 1

    def _get_all_categories(self):
        """Returns a sorted list of all unique categories."""
        all_cats = set(PREDEFINED_CATEGORIES)
        for t in self.transactions:
            all_cats.add(t['category'])
        return sorted(list(all_cats))

    def _add_transaction(self, is_income=False):
        """Handles the logic for adding a new income or expense transaction."""
        UI.clear_screen()
        trans_type = "Income" if is_income else "Expense"
        UI.display_header(f"Add New {trans_type}")
        
        date = UI.get_validated_input("Enter date (YYYY-MM-DD): ", validate_date, "Invalid date format.")
        description = UI.get_validated_input("Enter description: ", validate_not_empty, "Description cannot be empty.")
        
        if is_income:
            amount = UI.get_validated_input(
                "Enter amount: ",
                lambda x: validate_amount(x, allow_negative=False),
                "Amount must be a positive number."
            )
            category = "Income"
        else:
            amount_val = UI.get_validated_input(
                "Enter amount: ",
                lambda x: validate_amount(x, allow_negative=False),
                "Amount must be a positive number."
            )
            amount = -amount_val  # Expenses are stored as negative values

            all_categories = [cat for cat in self._get_all_categories() if cat != "Income"]
            print("Available categories:", ", ".join(all_categories))
            category = UI.get_validated_input(
                "Enter category: ",
                lambda x: validate_category(x, all_categories),
                "Category cannot be empty."
            )

        new_transaction = {
            "id": self._get_next_transaction_id(),
            "date": date,
            "description": description,
            "amount": amount,
            "category": category
        }

        self.transactions.append(new_transaction)
        self.data_manager.save_transactions(self.transactions)
        UI.print_message(f"{trans_type} transaction added successfully!", "info")
        UI.press_enter_to_continue()

    def _add_income(self):
        self._add_transaction(is_income=True)

    def _add_expense(self):
        self._add_transaction(is_income=False)

    def _view_transactions_menu(self, transactions_to_view=None, title="All Transactions", pause=True):
        """Displays a list of transactions in a table."""
        UI.clear_screen()
        UI.display_header(title)
        
        transactions = transactions_to_view if transactions_to_view is not None else self.transactions
        
        if not transactions:
            UI.print_message("No transactions found.")
        else:
            # Sort by date for better readability
            sorted_transactions = sorted(transactions, key=lambda t: t['date'], reverse=True)
            display_data = [{
                'ID': t.get('id', 'N/A'),
                'Date': t['date'],
                'Description': t['description'],
                'Amount': f"{t['amount']:.2f}",
                'Category': t['category']
            } for t in sorted_transactions]
            
            headers = ['ID', 'Date', 'Description', 'Amount', 'Category']
            UI.print_table(headers, display_data)
        
        if pause:
            UI.press_enter_to_continue()
    
    def _edit_transaction(self):
        """Allows the user to edit an existing transaction."""
        UI.clear_screen()
        UI.display_header("Edit Transaction")

        if not self.transactions:
            UI.print_message("No transactions to edit.")
            UI.press_enter_to_continue()
            return
            
        self._view_transactions_menu(title="Select Transaction to Edit", pause=False)

        try:
            trans_id_str = input("\nEnter the ID of the transaction to edit (or press Enter to cancel): ")
            if not trans_id_str:
                UI.print_message("Edit cancelled.", "info")
                UI.press_enter_to_continue()
                return
            
            trans_id = int(trans_id_str)
            transaction_to_edit = next((t for t in self.transactions if t.get('id') == trans_id), None)
            
            if not transaction_to_edit:
                UI.print_message(f"Transaction with ID {trans_id} not found.", "error")
                UI.press_enter_to_continue()
                return

            print("\nEditing transaction. Press Enter to keep current value.")
            
            # Get new values, keeping old ones if input is empty
            new_date = input(f"Date ({transaction_to_edit['date']}): ") or transaction_to_edit['date']
            new_desc = input(f"Description ({transaction_to_edit['description']}): ") or transaction_to_edit['description']
            new_amount_str = input(f"Amount ({transaction_to_edit['amount']:.2f}): ")
            new_category = input(f"Category ({transaction_to_edit['category']}): ") or transaction_to_edit['category']

            # Validate new values
            try:
                validated_date = validate_date(new_date)
                validated_desc = validate_not_empty(new_desc)
                validated_amount = validate_amount(new_amount_str) if new_amount_str else transaction_to_edit['amount']
                validated_category = validate_category(new_category, self._get_all_categories())
            except ValueError as e:
                UI.print_message(f"Invalid input: {e}", "error")
                UI.press_enter_to_continue()
                return

            if UI.get_confirmation("Are you sure you want to save these changes?"):
                transaction_to_edit['date'] = validated_date
                transaction_to_edit['description'] = validated_desc
                transaction_to_edit['amount'] = validated_amount
                transaction_to_edit['category'] = validated_category
                
                self.data_manager.save_transactions(self.transactions)
                UI.print_message("Transaction updated successfully.", "info")
            else:
                UI.print_message("Edit cancelled.", "info")

        except ValueError:
            UI.print_message("Invalid ID. Please enter a number.", "error")

        UI.press_enter_to_continue()

    def _delete_transaction(self):
        """Allows the user to delete an existing transaction."""
        UI.clear_screen()
        UI.display_header("Delete Transaction")

        if not self.transactions:
            UI.print_message("No transactions to delete.")
            UI.press_enter_to_continue()
            return

        self._view_transactions_menu(title="Select Transaction to Delete", pause=False)
        
        try:
            trans_id_str = input("\nEnter the ID of the transaction to delete (or press Enter to cancel): ")
            if not trans_id_str:
                UI.print_message("Deletion cancelled.", "info")
                UI.press_enter_to_continue()
                return

            trans_id = int(trans_id_str)
            transaction_to_delete = next((t for t in self.transactions if t.get('id') == trans_id), None)
            
            if not transaction_to_delete:
                UI.print_message(f"Transaction with ID {trans_id} not found.", "error")
                UI.press_enter_to_continue()
                return

            if UI.get_confirmation(f"Are you sure you want to delete transaction {trans_id}?"):
                self.transactions = [t for t in self.transactions if t.get('id') != trans_id]
                self.data_manager.save_transactions(self.transactions)
                UI.print_message("Transaction deleted successfully.", "info")
            else:
                UI.print_message("Deletion cancelled.", "info")

        except ValueError:
            UI.print_message("Invalid ID. Please enter a number.", "error")
            
        UI.press_enter_to_continue()

    def _filter_transactions_menu(self):
        """Provides options to filter transactions by date or category."""
        UI.clear_screen()
        UI.display_header("Filter Transactions")
        print("1. Filter by Date Range")
        print("2. Filter by Category")
        print("3. Back to Main Menu")
        choice = input("Choose an option: ")
        
        if choice == '1':
            start_date = UI.get_validated_input("Enter start date (YYYY-MM-DD): ", validate_date, "Invalid date.")
            end_date = UI.get_validated_input("Enter end date (YYYY-MM-DD): ", validate_date, "Invalid date.")
            filtered = [t for t in self.transactions if start_date <= t['date'] <= end_date]
            self._view_transactions_menu(filtered, f"Transactions from {start_date} to {end_date}")
        elif choice == '2':
            print("Available categories:", ", ".join(self._get_all_categories()))
            category = UI.get_validated_input("Enter category to filter by: ", validate_not_empty, "Category cannot be empty.").title()
            filtered = [t for t in self.transactions if t['category'].lower() == category.lower()]
            self._view_transactions_menu(filtered, f"Transactions in Category: {category}")
        elif choice == '3':
            return
        else:
            UI.print_message("Invalid choice.", "error")
            UI.press_enter_to_continue()

    def _set_budget_goal(self):
        """Allows the user to set a monthly spending limit for a category."""
        UI.clear_screen()
        UI.display_header("Set Budget Goal")
        
        expense_categories = [c for c in self._get_all_categories() if c != "Income"]
        print("Available expense categories:", ", ".join(expense_categories))
        
        category = UI.get_validated_input(
            "Enter category to set a budget for: ",
            validate_not_empty,
            "Category cannot be empty."
        ).title()
        
        if category == "Income":
            UI.print_message("Cannot set a budget goal for the 'Income' category.", "error")
            UI.press_enter_to_continue()
            return

        limit = UI.get_validated_input(
            "Enter monthly spending limit: ",
            lambda x: validate_amount(x, allow_negative=False),
            "Limit must be a positive number."
        )

        self.budget_goals[category] = limit
        self.data_manager.save_budget_goals(self.budget_goals)
        
        UI.print_message(f"Budget for '{category}' set to ${limit:.2f}.", "info")
        UI.press_enter_to_continue()

    def _get_spending_for_month(self, year, month):
        """Calculates spending totals for a given month."""
        spending = defaultdict(float)
        for t in self.transactions:
            try:
                trans_date = datetime.strptime(t['date'], '%Y-%m-%d')
                if trans_date.year == year and trans_date.month == month and t['amount'] < 0:
                    spending[t['category']] += abs(t['amount'])
            except (ValueError, KeyError):
                continue # Skip malformed transactions
        return dict(spending)

    def _view_budget_status(self):
        """Displays current spending vs. budget goals for the current month."""
        UI.clear_screen()
        UI.display_header("Budget Status (Current Month)")
        
        now = datetime.now()
        current_spending = self._get_spending_for_month(now.year, now.month)
        
        all_budget_cats = set(self.budget_goals.keys()) | set(current_spending.keys())
        if not all_budget_cats:
            UI.print_message("No budget goals set and no spending this month.")
            UI.press_enter_to_continue()
            return
            
        display_data = []
        for category in sorted(list(all_budget_cats)):
            if category == 'Income': continue
            goal = self.budget_goals.get(category, 0.0)
            spent = current_spending.get(category, 0.0)
            remaining = goal - spent
            
            if goal > 0:
                percent_used = (spent / goal) * 100 if goal > 0 else 0
                status = "Over Budget" if spent > goal else "On Track"
            else:
                percent_used = 0
                status = "No Goal Set"

            display_data.append({
                'Category': category,
                'Budget': f"{goal:.2f}",
                'Spent': f"{spent:.2f}",
                'Remaining': f"{remaining:.2f}",
                'Status': status,
                '% Used': f"{percent_used:.1f}%"
            })
            
        headers = ['Category', 'Budget', 'Spent', 'Remaining', 'Status', '% Used']
        UI.print_table(headers, display_data)
        UI.press_enter_to_continue()
    
    def _generate_monthly_summary(self):
        """Generates and displays a summary report for a specific month."""
        UI.clear_screen()
        UI.display_header("Monthly Summary Report")
        
        try:
            year_month_str = input("Enter year and month (YYYY-MM): ")
            year, month = map(int, year_month_str.split('-'))
        except ValueError:
            UI.print_message("Invalid format. Please use YYYY-MM.", "error")
            UI.press_enter_to_continue()
            return

        month_transactions = [t for t in self.transactions if datetime.strptime(t['date'], '%Y-%m-%d').year == year and datetime.strptime(t['date'], '%Y-%m-%d').month == month]
        
        if not month_transactions:
            UI.print_message(f"No transactions found for {year_month_str}.")
            UI.press_enter_to_continue()
            return
            
        total_income = sum(t['amount'] for t in month_transactions if t['amount'] > 0)
        total_expenses = sum(abs(t['amount']) for t in month_transactions if t['amount'] < 0)
        net_savings = total_income - total_expenses
        
        spending_by_cat = self._get_spending_for_month(year, month)

        print(f"\n--- Summary for {year_month_str} ---")
        print(f"Total Income:   ${total_income:,.2f}")
        print(f"Total Expenses: ${total_expenses:,.2f}")
        print("-" * 30)
        print(f"Net Savings:    ${net_savings:,.2f}")
        print("-" * 30)
        
        if spending_by_cat:
            print("Expenses by Category:")
            for category, amount in sorted(spending_by_cat.items(), key=lambda item: item[1], reverse=True):
                print(f"  - {category}: ${amount:,.2f}")
        else:
            print("No expenses recorded for this month.")
            
        UI.press_enter_to_continue()

    def _generate_pie_chart(self):
        """Generates and displays an ASCII pie chart of spending for a month."""
        UI.clear_screen()
        UI.display_header("Spending Pie Chart")

        try:
            year_month_str = input("Enter year and month for chart (YYYY-MM): ")
            year, month = map(int, year_month_str.split('-'))
        except ValueError:
            UI.print_message("Invalid format. Please use YYYY-MM.", "error")
            UI.press_enter_to_continue()
            return

        spending_data = self._get_spending_for_month(year, month)
        if not spending_data:
            UI.print_message(f"No spending data for {year_month_str}.")
            UI.press_enter_to_continue()
            return

        total_spent = sum(spending_data.values())
        if total_spent == 0:
            UI.print_message(f"No spending data for {year_month_str}.")
            UI.press_enter_to_continue()
            return

        sorted_spending = sorted(spending_data.items(), key=lambda x: x[1], reverse=True)
        
        symbols = "●○■□▲△▼▽◆◇★☆"
        legend = []
        
        print(f"\nSpending Breakdown for {year_month_str} (Total: ${total_spent:.2f})")
        
        proportions = []
        for i, (category, amount) in enumerate(sorted_spending):
            percent = (amount / total_spent) * 100
            symbol = symbols[i % len(symbols)]
            legend.append(f" {symbol} {category}: ${amount:.2f} ({percent:.1f}%)")
            proportions.append(int(round(percent)))
            
        chart_str = ""
        current_symbol_index = 0
        for p in proportions:
            chart_str += symbols[current_symbol_index % len(symbols)] * (p // 2) # Scale down for display
            current_symbol_index += 1
        
        print("\n" + "="*50)
        # Wrap the chart string for better display
        for i in range(0, len(chart_str), 50):
            print(chart_str[i:i+50])
        print("="*50)

        print("\n--- Legend ---")
        for item in legend:
            print(item)

        UI.press_enter_to_continue()

    def _generate_bar_chart(self):
        """Generates and displays an ASCII bar chart of spending for a month."""
        UI.clear_screen()
        UI.display_header("Spending Bar Chart")
        
        try:
            year_month_str = input("Enter year and month for chart (YYYY-MM): ")
            year, month = map(int, year_month_str.split('-'))
        except ValueError:
            UI.print_message("Invalid format. Please use YYYY-MM.", "error")
            UI.press_enter_to_continue()
            return
            
        spending_data = self._get_spending_for_month(year, month)
        if not spending_data:
            UI.print_message(f"No spending data for {year_month_str}.")
            UI.press_enter_to_continue()
            return
            
        sorted_spending = sorted(spending_data.items(), key=lambda x: x[1], reverse=True)
        max_amount = max(spending_data.values()) if spending_data else 1
        max_bar_width = 50
        max_label_width = max((len(cat) for cat in spending_data.keys()), default=10)
        
        print(f"\nSpending Comparison for {year_month_str}")
        for category, amount in sorted_spending:
            bar_length = int((amount / max_amount) * max_bar_width) if max_amount > 0 else 0
            bar = '█' * bar_length
            label = category.ljust(max_label_width)
            print(f"{label} | {bar} ${amount:.2f}")

        UI.press_enter_to_continue()

    def _exit_app(self):
        """Sets the running flag to False to exit the main loop."""
        self.running = False
        print("\nThank you for using BudgetMaster. Goodbye!")


if __name__ == "__main__":
    app = BudgetMasterApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Exiting.")
        sys.exit(0)