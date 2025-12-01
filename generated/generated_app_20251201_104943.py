# budgetmaster.py

import json
import os
import datetime
import math
import collections

# ==============================================================================
# 1. Constants and Configuration
# ==============================================================================

class Constants:
    """Stores global constants and configuration for the application."""
    TRANSACTIONS_FILE = 'transactions.json'
    BUDGET_GOALS_FILE = 'budget_goals.json'
    PREDEFINED_CATEGORIES = [
        "Food", "Transport", "Entertainment", "Utilities", 
        "Healthcare", "Shopping", "Savings", "Income"
    ]
    DATE_FORMAT = "%Y-%m-%d"
    BAR_CHART_WIDTH = 50

# ==============================================================================
# 2. Data Persistence
# ==============================================================================

class DataManager:
    """Handles loading from and saving data to JSON files."""

    @staticmethod
    def load_data(filename, default_structure):
        """
        Loads data from a JSON file. If the file doesn't exist, it's created.

        Args:
            filename (str): The name of the file to load.
            default_structure: The data structure to return/write if the file is empty/new.

        Returns:
            The loaded data (list or dict).
        """
        if not os.path.exists(filename):
            DataManager.save_data(filename, default_structure)
            return default_structure
        
        try:
            with open(filename, 'r') as f:
                # Handle case where file exists but is empty
                content = f.read()
                if not content:
                    return default_structure
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filename}: {e}. Starting with empty data.")
            return default_structure

    @staticmethod
    def save_data(filename, data):
        """
        Saves data to a JSON file with pretty printing.

        Args:
            filename (str): The name of the file to save to.
            data: The data (list or dict) to be saved.
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving to {filename}: {e}")

# ==============================================================================
# 3. User Input Handling
# ==============================================================================

class InputHandler:
    """Provides robust, validated user input functions."""

    @staticmethod
    def get_string(prompt):
        """Gets a non-empty string from the user."""
        while True:
            value = input(f"{prompt}: ").strip()
            if value:
                return value
            print("Input cannot be empty. Please try again.")

    @staticmethod
    def get_float(prompt, allow_negative=False):
        """Gets a valid float from the user."""
        while True:
            try:
                value = float(input(f"{prompt}: "))
                if not allow_negative and value < 0:
                    print("Amount cannot be negative. Please enter a positive value.")
                    continue
                return value
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    @staticmethod
    def get_date(prompt):
        """Gets a valid date from the user in YYYY-MM-DD format."""
        while True:
            date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
            try:
                datetime.datetime.strptime(date_str, Constants.DATE_FORMAT)
                return date_str
            except ValueError:
                print(f"Invalid date format. Please use {Constants.DATE_FORMAT.replace('%', '')}.")
    
    @staticmethod
    def get_category(prompt, all_categories):
        """Gets a category from the user, allowing for new categories."""
        print("\nAvailable categories:")
        for i, cat in enumerate(all_categories, 1):
            print(f"  {i}. {cat}")
        print("You can also type a new category name.")

        while True:
            choice = input(f"{prompt}: ").strip()
            if not choice:
                print("Category cannot be empty. Please try again.")
                continue

            # Check if user entered a number corresponding to a category
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(all_categories):
                    return all_categories[idx]
                else:
                    print("Invalid number. Please choose from the list or type a new category name.")
            else:
                # User typed a new category name
                return choice.title()

    @staticmethod
    def get_integer_in_range(prompt, min_val, max_val):
        """Gets an integer from the user within a specified range."""
        while True:
            try:
                value = int(input(f"{prompt}: "))
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("Invalid input. Please enter a whole number.")

    @staticmethod
    def get_confirmation(prompt):
        """Gets a yes/no confirmation from the user."""
        while True:
            choice = input(f"{prompt} (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            if choice in ['n', 'no']:
                return False
            print("Invalid input. Please enter 'y' or 'n'.")

# ==============================================================================
# 4. Display and Formatting
# ==============================================================================

class DisplayFormatter:
    """Handles consistent output formatting for menus, tables, and messages."""

    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_header(title):
        """Prints a formatted header."""
        print("\n" + "=" * 50)
        print(f"| {title.center(46)} |")
        print("=" * 50)

    @staticmethod
    def print_menu(title, options):
        """Prints a numbered menu."""
        DisplayFormatter.print_header(title)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print("-" * 50)

    @staticmethod
    def print_table(headers, rows):
        """
        Formats and prints tabular data.

        Args:
            headers (list): A list of header strings.
            rows (list of lists): A list where each inner list represents a row.
        """
        if not rows:
            print("No data to display.")
            return

        # Calculate column widths
        num_columns = len(headers)
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                cell_len = len(str(cell))
                if cell_len > col_widths[i]:
                    col_widths[i] = cell_len

        # Create format string
        header_format = " | ".join([f"{{:<{w}}}" for w in col_widths])
        row_format = " | ".join([f"{{:<{w}}}" for w in col_widths])
        
        # Print header
        print(header_format.format(*headers))
        print("-+-".join(["-" * w for w in col_widths]))

        # Print rows
        for row in rows:
            print(row_format.format(*[str(cell) for cell in row]))

    @staticmethod
    def print_message(message, is_error=False):
        """Prints a standardized message."""
        prefix = "[ERROR] " if is_error else "[INFO] "
        print(f"\n{prefix}{message}")

# ==============================================================================
# 5. Core Logic - Managers
# ==============================================================================

class TransactionManager:
    """Manages all transaction-related operations."""

    def __init__(self, transactions_data):
        self.transactions = transactions_data
        # Ensure a unique ID for new transactions
        self._next_id = self._get_max_id() + 1

    def _get_max_id(self):
        """Finds the highest ID in the current transaction list."""
        if not self.transactions:
            return 0
        return max(t['id'] for t in self.transactions)

    def add_transaction(self, date, name, amount, category):
        """Adds a new transaction to the list."""
        transaction = {
            'id': self._next_id,
            'date': date,
            'name': name,
            'amount': amount,
            'category': category
        }
        self.transactions.append(transaction)
        self._next_id += 1
        DisplayFormatter.print_message("Transaction added successfully.")

    def get_all_transactions(self, sort_by_date=True):
        """Returns all transactions, optionally sorted by date."""
        if sort_by_date:
            return sorted(self.transactions, key=lambda t: t['date'], reverse=True)
        return self.transactions

    def get_transaction_by_id(self, transaction_id):
        """Finds a transaction by its unique ID."""
        for t in self.transactions:
            if t['id'] == transaction_id:
                return t
        return None

    def edit_transaction(self, transaction_id, new_data):
        """Updates an existing transaction's details."""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            transaction.update(new_data)
            DisplayFormatter.print_message("Transaction updated successfully.")
            return True
        DisplayFormatter.print_message("Transaction not found.", is_error=True)
        return False

    def delete_transaction(self, transaction_id):
        """Removes a transaction from the list."""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            self.transactions.remove(transaction)
            DisplayFormatter.print_message("Transaction deleted successfully.")
            return True
        DisplayFormatter.print_message("Transaction not found.", is_error=True)
        return False

    def filter_by_category(self, category):
        """Returns transactions matching a specific category."""
        return [t for t in self.transactions if t['category'].lower() == category.lower()]

    def filter_by_month(self, year, month):
        """Returns transactions for a specific year and month."""
        return [
            t for t in self.transactions 
            if datetime.datetime.strptime(t['date'], Constants.DATE_FORMAT).year == year and
               datetime.datetime.strptime(t['date'], Constants.DATE_FORMAT).month == month
        ]

    def get_all_categories(self):
        """Returns a sorted list of unique categories from transactions and predefined ones."""
        used_categories = {t['category'] for t in self.transactions}
        all_cats = set(Constants.PREDEFINED_CATEGORIES).union(used_categories)
        return sorted(list(all_cats))
        
    @staticmethod
    def get_spending_by_category(transactions):
        """Calculates total spending per category from a list of transactions."""
        spending = collections.defaultdict(float)
        for t in transactions:
            if t['amount'] < 0:  # Only count expenses
                spending[t['category']] += abs(t['amount'])
        return dict(sorted(spending.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def get_total_income(transactions):
        """Calculates total income from a list of transactions."""
        return sum(t['amount'] for t in transactions if t['amount'] > 0)

    @staticmethod
    def get_total_expenses(transactions):
        """Calculates total expenses from a list of transactions."""
        return sum(abs(t['amount']) for t in transactions if t['amount'] < 0)

class BudgetManager:
    """Manages budget goal setting and tracking."""
    
    def __init__(self, budget_data):
        self.goals = budget_data
    
    def set_budget_goal(self, category, limit):
        """Sets or updates a monthly spending limit for a category."""
        if limit < 0:
            DisplayFormatter.print_message("Budget limit cannot be negative.", is_error=True)
            return
        self.goals[category] = limit
        DisplayFormatter.print_message(f"Budget for '{category}' set to ${limit:.2f}.")

    def get_all_goals(self):
        """Returns all budget goals."""
        return self.goals

# ==============================================================================
# 6. Reports and Visualizations
# ==============================================================================

class ReportGenerator:
    """Generates formatted textual reports."""

    @staticmethod
    def generate_monthly_summary(year, month, transactions):
        """Generates a summary report for a given month."""
        month_name = datetime.date(year, month, 1).strftime('%B')
        DisplayFormatter.print_header(f"Monthly Summary for {month_name} {year}")

        if not transactions:
            print("No transactions found for this month.")
            return

        total_income = TransactionManager.get_total_income(transactions)
        total_expenses = TransactionManager.get_total_expenses(transactions)
        net_flow = total_income - total_expenses

        print(f"Total Income:   ${total_income:10.2f}")
        print(f"Total Expenses: ${total_expenses:10.2f}")
        print("-" * 30)
        print(f"Net Cash Flow:  ${net_flow:10.2f}")
        print("\n--- Spending by Category ---")
        
        spending_by_cat = TransactionManager.get_spending_by_category(transactions)
        if not spending_by_cat:
            print("No expenses recorded for this month.")
        else:
            headers = ["Category", "Amount Spent", "% of Total"]
            rows = []
            for category, amount in spending_by_cat.items():
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                rows.append([category, f"${amount:.2f}", f"{percentage:.1f}%"])
            DisplayFormatter.print_table(headers, rows)


class Visualizer:
    """Generates ASCII art charts for terminal display."""

    @staticmethod
    def generate_bar_chart(spending, budgets):
        """Displays an ASCII bar chart comparing spending across categories."""
        DisplayFormatter.print_header("Spending by Category (Bar Chart)")
        
        if not spending:
            print("No expense data to visualize.")
            return

        max_amount = max(spending.values()) if spending else 1
        max_label_len = max(len(cat) for cat in spending.keys()) if spending else 0

        for category, amount in spending.items():
            bar_len = int((amount / max_amount) * Constants.BAR_CHART_WIDTH)
            bar = '█' * bar_len
            
            budget_info = ""
            if category in budgets:
                budget = budgets[category]
                budget_info = f" / ${budget:.2f}"
                if amount > budget:
                    budget_info += " (OVER)"
            
            print(f"{category:<{max_label_len}} | {bar} ${amount:.2f}{budget_info}")

    @staticmethod
    def generate_pie_chart(spending):
        """Displays a simple block-style ASCII 'pie' chart."""
        DisplayFormatter.print_header("Spending Breakdown (Pie Chart)")

        if not spending:
            print("No expense data to visualize.")
            return

        total = sum(spending.values())
        if total == 0:
            print("Total spending is zero.")
            return
            
        symbols = "█▓▒░@#*+=-."
        legend = []
        chart_data = []
        
        current_symbol_idx = 0
        for category, amount in spending.items():
            percentage = (amount / total)
            symbol = symbols[current_symbol_idx % len(symbols)]
            legend.append(f"{symbol} = {category} ({percentage:.1%})")
            chart_data.append((symbol, int(round(percentage * 100))))
            current_symbol_idx += 1
            
        print("--- Chart ---")
        chart_str = "".join([symbol * count for symbol, count in chart_data])
        # Wrap the chart string for better display
        for i in range(0, len(chart_str), 50):
            print(chart_str[i:i+50])

        print("\n--- Legend ---")
        for item in legend:
            print(item)


# ==============================================================================
# 7. Main Application
# ==============================================================================

class BudgetMasterApp:
    """Orchestrates the main program flow, menus, and user actions."""

    def __init__(self):
        """Initializes all managers and loads data."""
        self.is_running = True
        
        # Load data
        transactions_data = DataManager.load_data(Constants.TRANSACTIONS_FILE, [])
        budget_data = DataManager.load_data(Constants.BUDGET_GOALS_FILE, {})

        # Initialize managers
        self.transaction_manager = TransactionManager(transactions_data)
        self.budget_manager = BudgetManager(budget_data)

    def run(self):
        """The main application loop."""
        while self.is_running:
            self._display_main_menu()
            choice = InputHandler.get_integer_in_range("Enter your choice", 1, 10)
            self._handle_menu_choice(choice)
            if self.is_running:
                input("\nPress Enter to continue...")

    def _display_main_menu(self):
        """Displays the main menu options."""
        DisplayFormatter.clear_screen()
        menu_options = [
            "Add Income", "Add Expense", "View All Transactions",
            "Edit Transaction", "Delete Transaction", "Set Budget Goal",
            "View Budget Status & Visuals", "Generate Monthly Summary",
            "Filter Transactions by Category", "Exit"
        ]
        DisplayFormatter.print_menu("BudgetMaster Main Menu", menu_options)

    def _save_transactions(self):
        """Saves the current state of transactions to file."""
        DataManager.save_data(Constants.TRANSACTIONS_FILE, self.transaction_manager.get_all_transactions(sort_by_date=False))

    def _save_budgets(self):
        """Saves the current state of budget goals to file."""
        DataManager.save_data(Constants.BUDGET_GOALS_FILE, self.budget_manager.get_all_goals())

    def _handle_menu_choice(self, choice):
        """Dispatches user choice to the appropriate handler method."""
        actions = {
            1: self._handle_add_income,
            2: self._handle_add_expense,
            3: self._handle_view_transactions,
            4: self._handle_edit_transaction,
            5: self._handle_delete_transaction,
            6: self._handle_set_budget,
            7: self._handle_view_budget_status,
            8: self._handle_monthly_summary,
            9: self._handle_filter_transactions,
            10: self._handle_exit
        }
        action = actions.get(choice)
        if action:
            action()
        else:
            DisplayFormatter.print_message("Invalid choice.", is_error=True)

    def _handle_add_income(self):
        DisplayFormatter.print_header("Add Income")
        date = InputHandler.get_date("Enter date")
        name = InputHandler.get_string("Enter name/description")
        amount = InputHandler.get_float("Enter amount", allow_negative=False)
        # Incomes are often just categorized as 'Income'
        category = "Income"
        self.transaction_manager.add_transaction(date, name, amount, category)
        self._save_transactions()

    def _handle_add_expense(self):
        DisplayFormatter.print_header("Add Expense")
        date = InputHandler.get_date("Enter date")
        name = InputHandler.get_string("Enter name/description")
        amount = InputHandler.get_float("Enter amount", allow_negative=False)
        all_categories = self.transaction_manager.get_all_categories()
        category = InputHandler.get_category("Choose or enter a category", all_categories)
        self.transaction_manager.add_transaction(date, name, -amount, category)
        self._save_transactions()

    def _handle_view_transactions(self, transactions_to_show=None, title="All Transactions"):
        """Displays a list of transactions."""
        DisplayFormatter.print_header(title)
        
        transactions = transactions_to_show
        if transactions is None:
            transactions = self.transaction_manager.get_all_transactions()
            
        headers = ["ID", "Date", "Name", "Category", "Amount"]
        rows = []
        for t in transactions:
            amount_str = f"${t['amount']:.2f}"
            rows.append([t['id'], t['date'], t['name'], t['category'], amount_str])
        
        DisplayFormatter.print_table(headers, rows)

    def _select_transaction(self):
        """Helper to display transactions and let user select one by ID."""
        self._handle_view_transactions()
        transactions = self.transaction_manager.get_all_transactions()
        if not transactions:
            return None
            
        while True:
            try:
                choice_id_str = input("Enter the ID of the transaction to select (or type 'back' to return): ")
                if choice_id_str.lower() == 'back':
                    return None
                choice_id = int(choice_id_str)
                transaction = self.transaction_manager.get_transaction_by_id(choice_id)
                if transaction:
                    return transaction
                else:
                    DisplayFormatter.print_message("No transaction with that ID found.", is_error=True)
            except ValueError:
                DisplayFormatter.print_message("Please enter a valid number.", is_error=True)

    def _handle_edit_transaction(self):
        DisplayFormatter.print_header("Edit Transaction")
        transaction = self._select_transaction()
        if not transaction:
            return

        print("\nEnter new details (leave blank to keep current value):")
        
        # Get new data
        new_date_str = input(f"New date ({transaction['date']}): ").strip()
        new_date = new_date_str if new_date_str else transaction['date']

        new_name = input(f"New name ({transaction['name']}): ").strip() or transaction['name']
        
        new_amount_str = input(f"New amount ({transaction['amount']:.2f}): ").strip()
        new_amount = float(new_amount_str) if new_amount_str else transaction['amount']
        
        all_categories = self.transaction_manager.get_all_categories()
        print(f"Current category: {transaction['category']}")
        new_category_str = input("New category (choose from list or type new): ").strip()
        new_category = transaction['category']
        if new_category_str:
            if new_category_str.isdigit():
                 idx = int(new_category_str) - 1
                 if 0 <= idx < len(all_categories):
                     new_category = all_categories[idx]
            else:
                new_category = new_category_str.title()

        # Confirmation
        if InputHandler.get_confirmation("Are you sure you want to save these changes?"):
            updates = {
                'date': new_date,
                'name': new_name,
                'amount': new_amount,
                'category': new_category
            }
            self.transaction_manager.edit_transaction(transaction['id'], updates)
            self._save_transactions()

    def _handle_delete_transaction(self):
        DisplayFormatter.print_header("Delete Transaction")
        transaction = self._select_transaction()
        if not transaction:
            return

        if InputHandler.get_confirmation(f"Are you sure you want to delete transaction #{transaction['id']} ({transaction['name']})?"):
            self.transaction_manager.delete_transaction(transaction['id'])
            self._save_transactions()

    def _handle_set_budget(self):
        DisplayFormatter.print_header("Set Budget Goal")
        all_categories = self.transaction_manager.get_all_categories()
        # Exclude 'Income' from budget setting
        expense_categories = [c for c in all_categories if c != "Income"]
        
        category = InputHandler.get_category("Choose category to set budget for", expense_categories)
        limit = InputHandler.get_float(f"Enter monthly budget for '{category}'", allow_negative=False)
        
        self.budget_manager.set_budget_goal(category, limit)
        self._save_budgets()

    def _handle_view_budget_status(self):
        DisplayFormatter.print_header("Budget Status")
        
        today = datetime.date.today()
        # Get transactions for the current month
        monthly_transactions = self.transaction_manager.filter_by_month(today.year, today.month)
        spending = self.transaction_manager.get_spending_by_category(monthly_transactions)
        budgets = self.budget_manager.get_all_goals()
        
        all_relevant_categories = sorted(list(set(spending.keys()).union(set(budgets.keys()))))
        
        if not all_relevant_categories:
            print("No budgets set and no expenses this month.")
            return
            
        headers = ["Category", "Spent", "Budget", "Remaining"]
        rows = []
        for cat in all_relevant_categories:
            spent_amount = spending.get(cat, 0.0)
            budget_amount = budgets.get(cat, 0.0)
            remaining = budget_amount - spent_amount if budget_amount > 0 else 0.0
            
            remaining_str = f"${remaining:.2f}"
            if budget_amount > 0 and spent_amount > budget_amount:
                remaining_str += " (Over)"
            elif budget_amount == 0:
                remaining_str = "N/A"
            
            rows.append([
                cat, 
                f"${spent_amount:.2f}", 
                f"${budget_amount:.2f}" if budget_amount > 0 else "Not set", 
                remaining_str
            ])

        DisplayFormatter.print_table(headers, rows)

        # Show visualizations
        Visualizer.generate_bar_chart(spending, budgets)
        Visualizer.generate_pie_chart(spending)

    def _handle_monthly_summary(self):
        DisplayFormatter.print_header("Generate Monthly Summary")
        today = datetime.date.today()
        try:
            year_str = input(f"Enter year (e.g., {today.year}): ")
            year = int(year_str) if year_str else today.year
            month_str = input(f"Enter month (1-12, e.g., {today.month}): ")
            month = int(month_str) if month_str else today.month
            
            if not (1 <= month <= 12):
                DisplayFormatter.print_message("Month must be between 1 and 12.", is_error=True)
                return
        except ValueError:
            DisplayFormatter.print_message("Invalid number for year or month.", is_error=True)
            return

        monthly_transactions = self.transaction_manager.filter_by_month(year, month)
        ReportGenerator.generate_monthly_summary(year, month, monthly_transactions)

    def _handle_filter_transactions(self):
        DisplayFormatter.print_header("Filter Transactions by Category")
        all_categories = self.transaction_manager.get_all_categories()
        category_to_filter = InputHandler.get_category("Choose category to filter by", all_categories)
        
        filtered = self.transaction_manager.filter_by_category(category_to_filter)
        
        self._handle_view_transactions(
            transactions_to_show=filtered, 
            title=f"Transactions for Category: {category_to_filter}"
        )

    def _handle_exit(self):
        """Sets the flag to exit the application loop."""
        print("Thank you for using BudgetMaster. Goodbye!")
        self.is_running = False

# ==============================================================================
# 9. Test Cases (Documentation)
# ==============================================================================

"""
TESTING REQUIREMENTS DOCUMENTATION

Here are 10 test cases covering the application's core functionality.

1. Test Case: Add Transactions & View All
   - Steps:
     1. Start the application with no existing .json files.
     2. Select "Add Income". Enter date: 2023-10-01, name: "Paycheck", amount: 3000.
     3. Select "Add Expense". Enter date: 2023-10-02, name: "Groceries", amount: 150, category: "Food".
     4. Select "Add Expense". Enter date: 2023-10-03, name: "New Keyboard", amount: 80, category: "Electronics" (a new category).
     5. Select "View All Transactions".
   - Expected Result:
     - A table is displayed showing all three transactions with correct details.
     - The "Electronics" category is successfully added and displayed.
     - Income amount is positive, expense amounts are negative in the data model but shown as positive in user inputs.

2. Test Case: Edit an Existing Transaction
   - Steps:
     1. Add at least two transactions as in Test Case 1.
     2. Select "Edit Transaction".
     3. When prompted, enter the ID of the "Groceries" transaction.
     4. Change the amount to -165.50 and leave other fields blank.
     5. Confirm the changes.
     6. Select "View All Transactions".
   - Expected Result: The "Groceries" transaction now shows an amount of $-165.50.

3. Test Case: Delete a Transaction with Confirmation
   - Steps:
     1. Add three transactions.
     2. Select "Delete Transaction".
     3. Enter the ID of the second transaction.
     4. Confirm deletion by entering 'y'.
     5. Select "View All Transactions".
   - Expected Result: The list of transactions now contains only the first and third transactions.

4. Test Case: Set and View Budget Goals
   - Steps:
     1. Add expenses: "Food" ($150), "Transport" ($80), "Entertainment" ($50).
     2. Select "Set Budget Goal". Set "Food" budget to 400.
     3. Select "Set Budget Goal". Set "Entertainment" budget to 40.
     4. Select "View Budget Status & Visuals".
   - Expected Result:
     - A table shows current spending vs. budget.
     - For "Food", it shows Spent: $150.00, Budget: $400.00, Remaining: $250.00.
     - For "Entertainment", it shows Spent: $50.00, Budget: $40.00, Remaining: $-10.00 (Over).
     - ASCII charts are displayed reflecting this data.

5. Test Case: Generate Monthly Summary Report
   - Steps:
     1. Add transactions for the current month (e.g., October 2023) and a previous month (e.g., September 2023).
     2. Select "Generate Monthly Summary".
     3. Enter the year and month for the current month.
   - Expected Result: The report accurately shows total income, expenses, and a category breakdown using *only* the transactions from the specified month.

6. Test Case: Data Persistence (Save & Load)
   - Steps:
     1. Start the application.
     2. Add one income transaction and set one budget goal.
     3. Select "Exit".
     4. Relaunch the application.
     5. Select "View All Transactions".
     6. Select "View Budget Status & Visuals".
   - Expected Result:
     - The transaction added in the previous session is displayed.
     - The budget goal set in the previous session is correctly applied.
     - 'transactions.json' and 'budget_goals.json' files exist and contain the data.

7. Test Case: Input Validation - Invalid Amount
   - Steps:
     1. Select "Add Expense".
     2. At the "Enter amount" prompt, type "one hundred".
   - Expected Result: An error message "Invalid input. Please enter a valid number." is shown, and the prompt for the amount reappears.

8. Test Case: Input Validation - Invalid Date Format
   - Steps:
     1. Select "Add Income".
     2. At the "Enter date" prompt, type "10-25-2023".
   - Expected Result: An error message "Invalid date format. Please use YYYY-MM-DD." is shown, and the prompt for the date reappears.

9. Test Case: Filtering Transactions by Category
   - Steps:
     1. Add three "Food" transactions and two "Transport" transactions.
     2. Select "Filter Transactions by Category".
     3. Choose the "Food" category.
   - Expected Result: A table is displayed showing only the three "Food" transactions.

10. Test Case: No Data Scenario
    - Steps:
      1. Ensure no .json files exist. Start the application.
      2. Select "View All Transactions".
      3. Select "View Budget Status & Visuals".
      4. Select "Generate Monthly Summary" for the current month.
    - Expected Result:
      - For all options, a message like "No data to display." or "No transactions found..." is shown.
      - The application does not crash.
      - Empty 'transactions.json' and 'budget_goals.json' files are created.
"""

# ==============================================================================
# 10. Application Entry Point
# ==============================================================================

if __name__ == "__main__":
    app = BudgetMasterApp()
    app.run()