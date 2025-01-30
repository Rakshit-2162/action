import sqlite3
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('banking_system2.db')
cursor = conn.cursor()

# Create table for accounts
cursor.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    name TEXT,
    balance REAL
)
''')

# Create table for transactions
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

# Function to create a new account
def create_account(name, balance):
    cursor.execute('''
    INSERT INTO accounts (name, balance)
    VALUES (?, ?)
    ''', (name, balance))
    conn.commit()
    print(f"Account for {name} created successfully!")

# Function to record a transaction
def record_transaction(account_id, transaction_type, amount, source_account_id=None, target_account_id=None):
    transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO transactions (account_id, transaction_type, amount, source_account_id, target_account_id, transaction_date)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (account_id, transaction_type, amount, source_account_id, target_account_id, transaction_date))
    conn.commit()

# Function to get the transaction history for a particular account
def get_transaction_history(account_id):
    cursor.execute('''
    SELECT * FROM transactions WHERE account_id = ? ORDER BY transaction_date DESC
    ''', (account_id,))
    transactions = cursor.fetchall()
    if transactions:
        print(f"\nTransaction History for Account ID {account_id}:")
        for transaction in transactions:
            print(f"ID: {transaction[0]}, Type: {transaction[2]}, Amount: {transaction[3]}, Date: {transaction[6]}")
            if transaction[4] is not None:
                print(f"From Account ID: {transaction[4]}")
            if transaction[5] is not None:
                print(f"To Account ID: {transaction[5]}")
            print("-" * 40)
    else:
        print(f"No transactions found for Account ID {account_id}.")

# Function to update account balance (for adding funds)
def add_balance(id, amount):
    cursor.execute('''
    UPDATE accounts
    SET balance = balance + ?
    WHERE id = ?
    ''', (amount, id))
    conn.commit()
    print(f"{amount} added to account ID {id}. Updated balance: {get_balance(id)}")
    record_transaction(id, 'Deposit', amount)

# Function to withdraw money from an account
def withdraw_money(id, amount):
    current_balance = get_balance(id)
    if current_balance is None:
        print("Account does not exist.")
        return
    if amount > current_balance:
        print("Insufficient funds! Withdrawal exceeds balance.")
    else:
        cursor.execute('''
        UPDATE accounts
        SET balance = balance - ?
        WHERE id = ?
        ''', (amount, id))
        conn.commit()
        print(f"{amount} withdrawn from account ID {id}. Updated balance: {get_balance(id)}")
        record_transaction(id, 'Withdrawal', amount)

# Function to transfer funds between accounts
def transfer_funds(from_id, to_id, amount):
    from_balance = get_balance(from_id)
    to_balance = get_balance(to_id)

    if from_balance is None or to_balance is None:
        print("One of the accounts does not exist.")
        return

    if from_balance < amount:
        print("Insufficient funds in the source account!")
    else:
        cursor.execute('''
        UPDATE accounts
        SET balance = balance - ?
        WHERE id = ?
        ''', (amount, from_id))
        cursor.execute('''
        UPDATE accounts
        SET balance = balance + ?
        WHERE id = ?
        ''', (amount, to_id))
        conn.commit()
        print(f"{amount} transferred from account ID {from_id} to account ID {to_id}.")
        print(f"Updated balance for account {from_id}: {get_balance(from_id)}")
        print(f"Updated balance for account {to_id}: {get_balance(to_id)}")
        record_transaction(from_id, 'Transfer', amount, from_id, to_id)
        record_transaction(to_id, 'Transfer', amount, from_id, to_id)

# Function to get the current balance of an account
def get_balance(id):
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None

# Function to delete an account
def delete_account(id):
    cursor.execute('''
    DELETE FROM accounts WHERE id = ?
    ''', (id,))
    conn.commit()
    print(f"Account ID {id} deleted successfully!")

# Function to get account details (name and balance)
def get_account(id):
    cursor.execute('SELECT name, balance FROM accounts WHERE id = ?', (id,))
    result = cursor.fetchone()
    if result:
        print(f"\nAccount Details for Account ID {id}:")
        print(f"Name: {result[0]}")
        print(f"Balance: {result[1]}")
    else:
        print(f"Account with ID {id} does not exist.")

# Function to display menu and handle user input
def show_menu():
    while True:
        print("\nBanking System Menu:")
        print("1: Create Account")
        print("2: Add Balance")
        print("3: View Account Details")
        print("4: Transfer Funds")
        print("5: Withdraw Money")
        print("6: Delete Account")
        print("7: View Transaction History")
        print("8: Exit")

        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            name = input("Enter account holder's name: ")
            balance = float(input("Enter initial deposit amount: "))
            create_account(name, balance)

        elif choice == '2':
            account_id = int(input("Enter account ID: "))
            amount = float(input("Enter amount to add: "))
            add_balance(account_id, amount)

        elif choice == '3':
            account_id = int(input("Enter account ID: "))
            get_account(account_id)

        elif choice == '4':
            from_id = int(input("Enter source account ID: "))
            to_id = int(input("Enter target account ID: "))
            amount = float(input("Enter amount to transfer: "))
            transfer_funds(from_id, to_id, amount)

        elif choice == '5':
            account_id = int(input("Enter account ID: "))
            amount = float(input("Enter amount to withdraw: "))
            withdraw_money(account_id, amount)

        elif choice == '6':
            account_id = int(input("Enter account ID to delete: "))
            delete_account(account_id)

        elif choice == '7':
            account_id = int(input("Enter account ID to view transaction history: "))
            get_transaction_history(account_id)

        elif choice == '8':
            print("Exiting the banking system. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

# Start the banking system
show_menu()

# Close the connection when done
conn.close()