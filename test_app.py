import sqlite3
import pytest
from datetime import datetime

# Code of your banking system here (imported or copied directly)

# Set up a test database for testing purposes
@pytest.fixture(scope="module")
def setup_database():
    # Connect to a temporary database for testing
    conn = sqlite3.connect(':memory:')  # In-memory database for testing
    cursor = conn.cursor()

    # Create tables for testing
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
        transaction_type TEXT,
        amount REAL,
        source_account_id INTEGER,
        target_account_id INTEGER,
        transaction_date TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts (id),
        FOREIGN KEY (source_account_id) REFERENCES accounts (id),
        FOREIGN KEY (target_account_id) REFERENCES accounts (id)
    )
    ''')

    conn.commit()
    yield cursor, conn  # Return the cursor and connection for use in tests
    conn.close()  # Clean up and close the database after tests

# Test creating an account
def test_create_account(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    conn.commit()
    
    cursor.execute('SELECT * FROM accounts WHERE name = ?', ("John Doe",))
    account = cursor.fetchone()
    
    assert account is not None
    assert account[1] == "John Doe"
    assert account[2] == 500.0

# Test adding balance
def test_add_balance(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    conn.commit()
    
    account_id = cursor.lastrowid
    # Add balance to the account
    cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (200.0, account_id))
    conn.commit()
    
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    balance = cursor.fetchone()[0]
    
    assert balance == 700.0

# Test withdrawing money
def test_withdraw_money(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    conn.commit()
    
    account_id = cursor.lastrowid
    # Withdraw money from the account
    cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (100.0, account_id))
    conn.commit()
    
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    balance = cursor.fetchone()[0]
    
    assert balance == 400.0

# Test transferring funds between accounts
def test_transfer_funds(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("Jane Doe", 300.0))
    conn.commit()
    
    from_account_id = cursor.lastrowid - 1
    to_account_id = cursor.lastrowid
    
    # Transfer funds from John to Jane
    cursor.execute('UPDATE accounts SET balance = balance - ? WHERE id = ?', (100.0, from_account_id))
    cursor.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', (100.0, to_account_id))
    conn.commit()
    
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (from_account_id,))
    from_balance = cursor.fetchone()[0]
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (to_account_id,))
    to_balance = cursor.fetchone()[0]
    
    assert from_balance == 400.0
    assert to_balance == 400.0

# Test transaction history
def test_transaction_history(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    conn.commit()
    
    account_id = cursor.lastrowid
    # Record a deposit transaction
    cursor.execute('INSERT INTO transactions (account_id, transaction_type, amount, transaction_date) VALUES (?, ?, ?, ?)',
                   (account_id, 'Deposit', 200.0, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    
    cursor.execute('SELECT * FROM transactions WHERE account_id = ?', (account_id,))
    transactions = cursor.fetchall()
    
    assert len(transactions) == 1
    assert transactions[0][2] == 'Deposit'
    assert transactions[0][3] == 200.0

# Test getting account balance
def test_get_balance(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    conn.commit()
    
    account_id = cursor.lastrowid
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,))
    balance = cursor.fetchone()[0]
    
    assert balance == 500.0

# Test deleting an account
def test_delete_account(setup_database):
    cursor, conn = setup_database
    cursor.execute('INSERT INTO accounts (name, balance) VALUES (?, ?)', ("John Doe", 500.0))
    conn.commit()
    
    account_id = cursor.lastrowid
    # Delete the account
    cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    conn.commit()
    
    cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
    account = cursor.fetchone()
    
    assert account is None

# Run tests
if __name__ == "__main__":
    pytest.main()