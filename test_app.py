import sqlite3
import pytest
from io import StringIO
import sys

# Assuming all functions from your code are in a file called 'banking_system.py'
from banking_system import create_account, get_account, get_all_accounts, withdraw_money, deposit_money, show_transactions, delete_account, clear_database


@pytest.fixture(scope="module")
def setup_database():
    # Setup: create a new in-memory database for testing
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY,
        name TEXT,
        balance REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        account_id INTEGER,
        amount REAL,
        transaction_type TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
    )
    ''')

    conn.commit()

    # Return the connection and cursor for use in tests
    yield conn, cursor

    # Teardown: close the connection after tests
    conn.close()


def test_create_account(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)

    cursor.execute('SELECT * FROM accounts WHERE name = "Test User"')
    account = cursor.fetchone()
    assert account is not None
    assert account[1] == "Test User"
    assert account[2] == 100.0


def test_get_account(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)
    cursor.execute('SELECT id FROM accounts WHERE name = "Test User"')
    account_id = cursor.fetchone()[0]

    # Test getting account details
    output = StringIO()
    sys.stdout = output
    get_account(account_id)
    sys.stdout = sys.__stdout__
    output_value = output.getvalue().strip()

    assert "Account ID" in output_value
    assert "Test User" in output_value
    assert "100.0" in output_value


def test_withdraw_money(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)
    cursor.execute('SELECT id FROM accounts WHERE name = "Test User"')
    account_id = cursor.fetchone()[0]

    # Withdraw money
    withdraw_money(account_id, 50.0)

    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    new_balance = cursor.fetchone()[0]
    assert new_balance == 50.0

    cursor.execute('SELECT * FROM transactions WHERE account_id = ?', (account_id,))
    transaction = cursor.fetchone()
    assert transaction is not None
    assert transaction[3] == 'withdraw'
    assert transaction[2] == 50.0


def test_deposit_money(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)
    cursor.execute('SELECT id FROM accounts WHERE name = "Test User"')
    account_id = cursor.fetchone()[0]

    # Deposit money
    deposit_money(account_id, 50.0)

    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    new_balance = cursor.fetchone()[0]
    assert new_balance == 150.0

    cursor.execute('SELECT * FROM transactions WHERE account_id = ?', (account_id,))
    transaction = cursor.fetchone()
    assert transaction is not None
    assert transaction[3] == 'deposit'
    assert transaction[2] == 50.0


def test_show_transactions(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)
    cursor.execute('SELECT id FROM accounts WHERE name = "Test User"')
    account_id = cursor.fetchone()[0]

    # Deposit and withdraw some money
    deposit_money(account_id, 50.0)
    withdraw_money(account_id, 30.0)

    # Test showing transactions
    output = StringIO()
    sys.stdout = output
    show_transactions(account_id)
    sys.stdout = sys.__stdout__
    output_value = output.getvalue().strip()

    assert "Transaction ID" in output_value
    assert "deposit" in output_value
    assert "withdraw" in output_value
    assert "50.0" in output_value
    assert "30.0" in output_value


def test_delete_account(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)
    cursor.execute('SELECT id FROM accounts WHERE name = "Test User"')
    account_id = cursor.fetchone()[0]

    # Delete the account
    delete_account(account_id)

    cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
    account = cursor.fetchone()
    assert account is None

    cursor.execute('SELECT * FROM transactions WHERE account_id = ?', (account_id,))
    transactions = cursor.fetchall()
    assert len(transactions) == 0


def test_clear_database(setup_database):
    conn, cursor = setup_database

    create_account("Test User", 100.0)
    create_account("Test User 2", 200.0)

    clear_database()

    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    assert len(accounts) == 0

    cursor.execute('SELECT * FROM transactions')
    transactions = cursor.fetchall()
    assert len(transactions) == 0
