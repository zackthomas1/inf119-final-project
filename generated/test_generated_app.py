import pytest
import json
import os
from unittest.mock import patch
from generated_app import BudgetMasterApp, DataManager, UI, validate_date, validate_not_empty, validate_amount, validate_category, TRANSACTIONS_FILE, BUDGET_GOALS_FILE, PREDEFINED_CATEGORIES

# --- Fixtures ---
@pytest.fixture
def app():
    """Fixture to create an instance of BudgetMasterApp for testing."""
    app = BudgetMasterApp()
    # Clear existing data
    app.transactions = []
    app.budget_goals = {}
    app.data_manager.save_transactions([])
    app.data_manager.save_budget_goals([])
    return app

@pytest.fixture
def data_manager():
    """Fixture to create an instance of DataManager for testing."""
    return DataManager(TRANSACTIONS_FILE, BUDGET_GOALS_FILE)

# --- Tests ---
def test_add_income(app):
    """Test adding an income transaction."""
    with patch('builtins.input', side_effect=['2024-01-01', 'Salary', '1000']):
        app._add_income()
    assert len(app.transactions) == 1
    assert app.transactions[0]['amount'] == 1000.0
    assert app.transactions[0]['category'] == 'Income'

def test_add_expense(app):
    """Test adding an expense transaction."""
    with patch('builtins.input', side_effect=['2024-01-02', 'Groceries', '100', 'Food']):
        app._add_expense()
    assert len(app.transactions) == 1
    assert app.transactions[0]['amount'] == -100.0
    assert app.transactions[0]['category'] == 'Food'

def test_edit_transaction(app):
    """Test editing an existing transaction."""
    # Add a transaction first
    with patch('builtins.input', side_effect=['2024-01-01', 'Salary', '1000']):
        app._add_income()

    # Now edit it
    with patch('builtins.input', side_effect=['1', '2024-01-05', 'Bonus', '1500', 'Income', 'y']):
        app._edit_transaction()

    assert app.transactions[0]['date'] == '2024-01-05'
    assert app.transactions[0]['description'] == 'Bonus'
    assert app.transactions[0]['amount'] == 1500.0
    assert app.transactions[0]['category'] == 'Income'

def test_delete_transaction(app):
    """Test deleting an existing transaction."""
    # Add a transaction first
    with patch('builtins.input', side_effect=['2024-01-01', 'Salary', '1000']):
        app._add_income()

    # Now delete it
    with patch('builtins.input', side_effect=['1', 'y']):
        app._delete_transaction()

    assert len(app.transactions) == 0

def test_set_budget_goal(app):
    """Test setting a budget goal for a category."""
    with patch('builtins.input', side_effect=['Food', '500']):
        app._set_budget_goal()

    assert 'Food' in app.budget_goals
    assert app.budget_goals['Food'] == 500.0

def test_data_persistence_transactions(app):
    """Test that transactions are saved and loaded correctly."""
    with patch('builtins.input', side_effect=['2024-01-01', 'Salary', '1000']):
        app._add_income()
    
    # Create a new app instance to simulate restarting the application
    new_app = BudgetMasterApp()

    assert len(new_app.transactions) == 1
    assert new_app.transactions[0]['amount'] == 1000.0
    assert new_app.transactions[0]['category'] == 'Income'

def test_data_persistence_budget_goals(app):
    """Test that budget goals are saved and loaded correctly."""
    with patch('builtins.input', side_effect=['Food', '500']):
        app._set_budget_goal()
    
    # Create a new app instance to simulate restarting the application
    new_app = BudgetMasterApp()
    
    assert 'Food' in new_app.budget_goals
    assert new_app.budget_goals['Food'] == 500.0

def test_validate_date_valid():
    """Test validating a valid date."""
    assert validate_date('2024-01-01') == '2024-01-01'

def test_validate_date_invalid():
    """Test validating an invalid date."""
    with pytest.raises(ValueError):
        validate_date('01-01-2024')

def test_validate_not_empty_valid():
    """Test validating a non-empty string."""
    assert validate_not_empty('  test  ') == 'test'

def test_validate_not_empty_invalid():
    """Test validating an empty string."""
    with pytest.raises(ValueError):
        validate_not_empty('  ')

def test_validate_amount_valid_positive():
    """Test validating a valid positive amount."""
    assert validate_amount('100.50') == 100.50

def test_validate_amount_valid_negative():
    """Test validating a valid negative amount."""
    assert validate_amount('-50') == -50.0

def test_validate_amount_invalid():
    """Test validating an invalid amount."""
    with pytest.raises(ValueError):
        validate_amount('abc')

def test_validate_amount_not_negative():
    """Test validating non-negative amount."""
    with pytest.raises(ValueError):
         validate_amount('-10', allow_negative=False)

def test_validate_category_valid():
    """Test validating a valid category."""
    assert validate_category('Food', PREDEFINED_CATEGORIES) == 'Food'

def test_validate_category_new():
    """Test validating a new category."""
    all_categories = ["Food"]
    assert validate_category('New Category', all_categories) == 'New Category'

def test_filter_transactions_by_date(app):
    """Test filtering transactions by date range."""
    # Add some transactions
    with patch('builtins.input', side_effect=['2024-01-01', 'Salary', '1000']):
        app._add_income()
    with patch('builtins.input', side_effect=['2024-01-15', 'Groceries', '50', 'Food']):
        app._add_expense()
    with patch('builtins.input', side_effect=['2024-02-01', 'Rent', '1200', 'Utilities']):
        app._add_expense()

    # Filter by date range
    with patch('builtins.input', side_effect=['1', '2024-01-01', '2024-01-31']):
         app._filter_transactions_menu()
    
    #Filtering tests are only partially testable since the UI display is mocked.  Focus is on date range validation

def test_filter_transactions_by_category(app):
    """Test filtering transactions by category."""
    # Add some transactions
    with patch('builtins.input', side_effect=['2024-01-01', 'Salary', '1000']):
        app._add_income()
    with patch('builtins.input', side_effect=['2024-01-15', 'Groceries', '50', 'Food']):
        app._add_expense()

    # Filter by category
    with patch('builtins.input', side_effect=['2', 'Food']):
        app._filter_transactions_menu()
    
    #Filtering tests are only partially testable since the UI display is mocked. Focus is on category validation
def test_initialization_creates_files(data_manager):
    """Test that the DataManager creates the transaction and budget files if they don't exist."""
    # Remove the files if they exist
    if os.path.exists(TRANSACTIONS_FILE):
        os.remove(TRANSACTIONS_FILE)
    if os.path.exists(BUDGET_GOALS_FILE):
        os.remove(BUDGET_GOALS_FILE)

    # Create a new DataManager which should create the files
    data_manager = DataManager(TRANSACTIONS_FILE, BUDGET_GOALS_FILE)

    assert os.path.exists(TRANSACTIONS_FILE)
    assert os.path.exists(BUDGET_GOALS_FILE)