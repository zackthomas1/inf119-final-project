import pytest
import json
import os
from datetime import datetime
from generated_app_20251201_104943 import BudgetMasterApp, TransactionManager, DataManager, Constants

# Test Data
TEST_TRANSACTIONS_FILE = 'test_transactions.json'
TEST_BUDGET_GOALS_FILE = 'test_budget_goals.json'

# Utility Functions
def clear_test_data():
    """Removes test data files if they exist."""
    if os.path.exists(TEST_TRANSACTIONS_FILE):
        os.remove(TEST_TRANSACTIONS_FILE)
    if os.path.exists(TEST_BUDGET_GOALS_FILE):
        os.remove(TEST_BUDGET_GOALS_FILE)

def create_test_transactions(transactions):
    """Creates a test transactions file."""
    with open(TEST_TRANSACTIONS_FILE, 'w') as f:
        json.dump(transactions, f, indent=4)

def create_test_budget_goals(goals):
    """Creates a test budget goals file."""
    with open(TEST_BUDGET_GOALS_FILE, 'w') as f:
        json.dump(goals, f, indent=4)

# Fixtures
@pytest.fixture
def app():
    """Provides a clean BudgetMasterApp instance for each test."""
    clear_test_data()
    app = BudgetMasterApp()
    # Override file names for testing
    app.transaction_manager.transactions = DataManager.load_data(TEST_TRANSACTIONS_FILE, [])
    app.budget_manager.goals = DataManager.load_data(TEST_BUDGET_GOALS_FILE, {})

    Constants.TRANSACTIONS_FILE = TEST_TRANSACTIONS_FILE
    Constants.BUDGET_GOALS_FILE = TEST_BUDGET_GOALS_FILE
    yield app
    clear_test_data()

# Tests
def test_add_income_transaction(app):
    """Test adding an income transaction."""
    app._handle_add_income()
    transactions = DataManager.load_data(TEST_TRANSACTIONS_FILE, [])
    assert len(transactions) == 1
    assert transactions[0]['amount'] > 0

def test_add_expense_transaction(app, monkeypatch):
    """Test adding an expense transaction."""
    monkeypatch.setattr('builtins.input', lambda _: 'Food') #Mock category input
    app._handle_add_expense()
    transactions = DataManager.load_data(TEST_TRANSACTIONS_FILE, [])
    assert len(transactions) == 1
    assert transactions[0]['amount'] < 0

def test_view_all_transactions_empty(app, capsys):
    """Test viewing transactions when there are none."""
    app._handle_view_transactions()
    captured = capsys.readouterr()
    assert "No data to display." in captured.out

def test_edit_transaction(app, monkeypatch):
    """Test editing an existing transaction."""
    test_data = [{'id': 1, 'date': '2023-10-26', 'name': 'Test', 'amount': 100, 'category': 'Food'}]
    create_test_transactions(test_data)
    app.transaction_manager = TransactionManager(DataManager.load_data(TEST_TRANSACTIONS_FILE, [])) #Reload transaction manager

    # Mock user input for transaction selection and edits
    monkeypatch.setattr('builtins.input', lambda prompt: '1' if 'ID' in prompt else '2023-11-01' if 'New date' in prompt else 'Edited Test' if 'New name' in prompt else '150' if 'New amount' in prompt else 'Food' if 'New category' in prompt else 'y')
    app._handle_edit_transaction()
    transactions = DataManager.load_data(TEST_TRANSACTIONS_FILE, [])
    assert transactions[0]['date'] == '2023-11-01'
    assert transactions[0]['name'] == 'Edited Test'
    assert transactions[0]['amount'] == 150

def test_delete_transaction(app, monkeypatch):
    """Test deleting a transaction."""
    test_data = [{'id': 1, 'date': '2023-10-26', 'name': 'Test', 'amount': 100, 'category': 'Food'}]
    create_test_transactions(test_data)
    app.transaction_manager = TransactionManager(DataManager.load_data(TEST_TRANSACTIONS_FILE, [])) #Reload transaction manager

    monkeypatch.setattr('builtins.input', lambda prompt: '1' if 'ID' in prompt else 'y') #Mock user input for transaction selection and confirmation
    app._handle_delete_transaction()
    transactions = DataManager.load_data(TEST_TRANSACTIONS_FILE, [])
    assert len(transactions) == 0

def test_set_budget_goal(app, monkeypatch):
    """Test setting a budget goal."""
    monkeypatch.setattr('builtins.input', lambda prompt: 'Food' if 'category' in prompt else '200') #Mock user input
    app._handle_set_budget()
    budgets = DataManager.load_data(TEST_BUDGET_GOALS_FILE, {})
    assert 'Food' in budgets
    assert budgets['Food'] == 200

def test_view_budget_status_empty(app, capsys):
    """Test viewing budget status when no budgets are set and no expenses."""
    app._handle_view_budget_status()
    captured = capsys.readouterr()
    assert "No budgets set and no expenses this month." in captured.out

def test_monthly_summary_report_no_transactions(app, capsys):
    """Test generating a monthly summary when there are no transactions."""
    app._handle_monthly_summary()
    captured = capsys.readouterr()
    assert "No transactions found for this month." in captured.out

def test_filter_transactions_by_category(app):
    """Test filtering transactions by category."""
    test_data = [
        {'id': 1, 'date': '2023-10-26', 'name': 'Food1', 'amount': -50, 'category': 'Food'},
        {'id': 2, 'date': '2023-10-27', 'name': 'Transport1', 'amount': -30, 'category': 'Transport'},
        {'id': 3, 'date': '2023-10-28', 'name': 'Food2', 'amount': -75, 'category': 'Food'}
    ]
    create_test_transactions(test_data)
    app.transaction_manager = TransactionManager(DataManager.load_data(TEST_TRANSACTIONS_FILE, [])) #Reload transaction manager
    filtered = app.transaction_manager.filter_by_category('Food')
    assert len(filtered) == 2
    for transaction in filtered:
        assert transaction['category'] == 'Food'

def test_data_persistence(app):
    """Test that data persists between app sessions."""
    # Add a transaction and a budget goal
    test_date = '2023-11-05'
    test_name = 'Initial Transaction'
    test_amount = 50.0
    test_category = "Food"

    app.transaction_manager.add_transaction(test_date, test_name, test_amount, test_category)
    app.budget_manager.set_budget_goal(test_category, 100.0)

    # Save the data
    app._save_transactions()
    app._save_budgets()

    # Create a new app instance
    new_app = BudgetMasterApp()
    new_app.transaction_manager.transactions = DataManager.load_data(TEST_TRANSACTIONS_FILE, [])
    new_app.budget_manager.goals = DataManager.load_data(TEST_BUDGET_GOALS_FILE, {})

    # Check if the data is loaded correctly
    transactions = new_app.transaction_manager.get_all_transactions()
    budgets = new_app.budget_manager.get_all_goals()

    assert len(transactions) == 1
    assert transactions[0]['date'] == test_date
    assert transactions[0]['name'] == test_name
    assert transactions[0]['amount'] == test_amount
    assert transactions[0]['category'] == test_category
    assert test_category in budgets
    assert budgets[test_category] == 100.0

def test_get_spending_by_category():
    """Tests the utility function get_spending_by_category."""
    transactions = [
        {'id': 1, 'date': '2023-11-01', 'name': 'Groceries', 'amount': -50, 'category': 'Food'},
        {'id': 2, 'date': '2023-11-01', 'name': 'Train', 'amount': -30, 'category': 'Transport'},
        {'id': 3, 'date': '2023-11-02', 'name': 'Dinner', 'amount': -60, 'category': 'Food'},
        {'id': 4, 'date': '2023-11-03', 'name': 'Salary', 'amount': 2000, 'category': 'Income'}
    ]
    spending = TransactionManager.get_spending_by_category(transactions)
    assert spending['Food'] == 110
    assert spending['Transport'] == 30
    assert len(spending) == 2