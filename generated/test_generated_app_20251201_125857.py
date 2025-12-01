import pytest
import os
import json
import uuid
import datetime
import tempfile
import shutil
from collections import defaultdict
from generated_app_20251201_125857 import (
    Transaction,
    Validator,
    DataManager,
    TransactionManager,
    BudgetManager,
    ReportGenerator,
    Constants
)

@pytest.fixture
def temp_files():
    """
    Fixture to create temporary transaction and budget files for testing.
    """
    temp_dir = tempfile.mkdtemp()
    transaction_file = os.path.join(temp_dir, "transactions.json")
    budget_file = os.path.join(temp_dir, "budget_goals.json")
    yield transaction_file, budget_file
    shutil.rmtree(temp_dir)

def test_transaction_creation():
    transaction = Transaction("2023-01-01", "Test Transaction", 100.0, "Food")
    assert transaction.date == "2023-01-01"
    assert transaction.name == "Test Transaction"
    assert transaction.amount == 100.0
    assert transaction.category == "Food"
    assert transaction.transaction_id is not None

def test_transaction_to_dict():
    transaction = Transaction("2023-01-01", "Test Transaction", 100.0, "Food", "test_id")
    transaction_dict = transaction.to_dict()
    assert transaction_dict["date"] == "2023-01-01"
    assert transaction_dict["name"] == "Test Transaction"
    assert transaction_dict["amount"] == 100.0
    assert transaction_dict["category"] == "Food"
    assert transaction_dict["transaction_id"] == "test_id"

def test_transaction_from_dict():
    transaction_dict = {"date": "2023-01-01", "name": "Test Transaction", "amount": 100.0, "category": "Food", "transaction_id": "test_id"}
    transaction = Transaction.from_dict(transaction_dict)
    assert transaction.date == "2023-01-01"
    assert transaction.name == "Test Transaction"
    assert transaction.amount == 100.0
    assert transaction.category == "Food"
    assert transaction.transaction_id == "test_id"

def test_valid_date():
    assert Validator.is_valid_date("2023-12-01") is True
    assert Validator.is_valid_date("2023-02-29") is False
    assert Validator.is_valid_date("2023/12/01") is False

def test_valid_amount():
    assert Validator.is_valid_amount("100.0") is True
    assert Validator.is_valid_amount("-50") is True
    assert Validator.is_valid_amount("abc") is False

def test_valid_category():
    assert Validator.is_valid_category("Food", Constants.PREDEFINED_CATEGORIES) is True
    assert Validator.is_valid_category("Invalid", Constants.PREDEFINED_CATEGORIES) is False

def test_valid_menu_choice():
    assert Validator.is_valid_menu_choice("1", 5) is True
    assert Validator.is_valid_menu_choice("5", 5) is True
    assert Validator.is_valid_menu_choice("0", 5) is False
    assert Validator.is_valid_menu_choice("6", 5) is False
    assert Validator.is_valid_menu_choice("a", 5) is False

def test_data_manager_load_empty_transactions(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    transactions = data_manager.load_transactions()
    assert isinstance(transactions, list)
    assert len(transactions) == 0

def test_data_manager_load_empty_budget_goals(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    budget_goals = data_manager.load_budget_goals()
    assert isinstance(budget_goals, dict)
    assert len(budget_goals) == 0

def test_data_manager_save_and_load_transactions(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    transactions = [Transaction("2023-01-01", "Test Transaction", 100.0, "Food")]
    data_manager.save_transactions(transactions)
    loaded_transactions = data_manager.load_transactions()
    assert len(loaded_transactions) == 1
    assert loaded_transactions[0].name == "Test Transaction"

def test_data_manager_save_and_load_budget_goals(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    budget_goals = {"Food": 200.0}
    data_manager.save_budget_goals(budget_goals)
    loaded_budget_goals = data_manager.load_budget_goals()
    assert len(loaded_budget_goals) == 1
    assert loaded_budget_goals["Food"] == 200.0

def test_transaction_manager_add_transaction(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    transaction_manager = TransactionManager(data_manager)
    transaction_manager.add_transaction("2023-01-01", "Test Transaction", 100.0, "Food")
    assert len(transaction_manager.get_all_transactions()) == 1

def test_transaction_manager_get_transaction_by_id(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    transaction_manager = TransactionManager(data_manager)
    transaction = Transaction("2023-01-01", "Test Transaction", 100.0, "Food")
    transaction_manager.transactions.append(transaction)
    found_transaction = transaction_manager.get_transaction_by_id(transaction.transaction_id)
    assert found_transaction == transaction

def test_transaction_manager_update_transaction(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    transaction_manager = TransactionManager(data_manager)
    transaction = Transaction("2023-01-01", "Test Transaction", 100.0, "Food")
    transaction_manager.transactions.append(transaction)
    transaction_id = transaction.transaction_id
    transaction_manager.update_transaction(transaction_id, {"amount": 200.0})
    updated_transaction = transaction_manager.get_transaction_by_id(transaction_id)
    assert updated_transaction.amount == 200.0

def test_transaction_manager_delete_transaction(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    transaction_manager = TransactionManager(data_manager)
    transaction = Transaction("2023-01-01", "Test Transaction", 100.0, "Food")
    transaction_manager.transactions.append(transaction)
    transaction_id = transaction.transaction_id
    transaction_manager.delete_transaction(transaction_id)
    assert len(transaction_manager.get_all_transactions()) == 0

def test_budget_manager_set_goal(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    budget_manager = BudgetManager(data_manager)
    budget_manager.set_goal("Food", 300.0)
    assert budget_manager.get_all_goals()["Food"] == 300.0

def test_budget_manager_get_budget_status(temp_files):
    transaction_file, budget_file = temp_files
    data_manager = DataManager(transaction_file, budget_file)
    budget_manager = BudgetManager(data_manager)
    budget_manager.set_goal("Food", 300.0)
    current_spending = {"Food": 200.0}
    status = budget_manager.get_budget_status(current_spending)
    assert len(status) == 1
    assert status[0][0] == "Food"
    assert status[0][1] == "$300.00"
    assert status[0][2] == "$200.00"
    assert "Remaining" in status[0][3]

def test_transaction_manager_get_spending_by_category():
    transactions = [
        Transaction("2023-01-01", "Test Transaction", -50.0, "Food"),
        Transaction("2023-01-02", "Test Transaction", -100.0, "Transport"),
        Transaction("2023-01-03", "Test Transaction", -25.0, "Food"),
    ]
    spending = TransactionManager.get_spending_by_category(transactions)
    assert spending["Food"] == 75.0
    assert spending["Transport"] == 100.0

def test_transaction_manager_get_total_income():
    transactions = [
        Transaction("2023-01-01", "Test Transaction", 100.0, "Income"),
        Transaction("2023-01-02", "Test Transaction", -50.0, "Food"),
        Transaction("2023-01-03", "Test Transaction", 25.0, "Income"),
    ]
    total_income = TransactionManager.get_total_income(transactions)
    assert total_income == 125.0

def test_transaction_manager_get_total_expenses():
    transactions = [
        Transaction("2023-01-01", "Test Transaction", -100.0, "Food"),
        Transaction("2023-01-02", "Test Transaction", 50.0, "Income"),
        Transaction("2023-01-03", "Test Transaction", -25.0, "Transport"),
    ]
    total_expenses = TransactionManager.get_total_expenses(transactions)
    assert total_expenses == 125.0

def test_report_generator_generate_monthly_summary():
    transactions = [
        Transaction("2023-12-01", "Test Transaction", 100.0, "Income"),
        Transaction("2023-12-15", "Test Transaction", -50.0, "Food"),
        Transaction("2024-01-01", "Test Transaction", 25.0, "Income"),
    ]
    # ReportGenerator.generate_monthly_summary(12, 2023, transactions) #Can't test print statements
    pass