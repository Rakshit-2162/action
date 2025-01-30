import sqlite3

conn = sqlite3.connect('banking_system.db')
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

def create_account(name, balance = 0.0):
    cursor.execute('''
    INSERT INTO accounts (name, balance)
    VALUES (?, ?)
    ''', (name, balance))
    conn.commit()
    print(f"\nAccount for {name} created successfully!")

def get_account(id):
    cursor.execute('SELECT * FROM accounts WHERE id = ?', (id,))
    account = cursor.fetchone()
    if account:
        print(f"\nAccount ID: {account[0]}, Name: {account[1]}, Balance: {account[2]}")
    else:
        print(f"\nNo account found with ID {id}")

def get_all_accounts():
    cursor.execute('SELECT * FROM accounts')
    account = cursor.fetchall()
    print("\nAll Accounts:")
    for i in account:
        print(f"Account ID: {i[0]}, Name: {i[1]}, Balance: {i[2]}")

def withdraw_money(id, amount):
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (id,))
    current_balance = cursor.fetchone()[0]
    if current_balance >= amount:
        new_balance = current_balance - amount
        cursor.execute('''
        UPDATE accounts SET balance = ? WHERE id = ?
        ''', (new_balance, id))
        cursor.execute('''
        INSERT INTO transactions (account_id, amount, transaction_type)
        VALUES (?, ?, ?)
        ''', (id, amount, 'withdraw'))
        conn.commit()
        print(f"\nWithdrew ${amount}. New balance: ${new_balance}")
    else:
        print("\nInsufficient amount!")

def deposit_money(id, amount):
    cursor.execute('SELECT balance FROM accounts WHERE id = ?', (id,))
    current_balance = cursor.fetchone()[0]
    new_balance = current_balance + amount
    cursor.execute('''
    UPDATE accounts SET balance = ? WHERE id = ?
    ''', (new_balance, id))
    cursor.execute('''
    INSERT INTO transactions (account_id, amount, transaction_type)
    VALUES (?, ?, ?)
    ''', (id, amount, 'deposit'))
    conn.commit()
    print(f"\nDeposited ${amount}. New balance: ${new_balance}")

def show_transactions(id):
    cursor.execute('SELECT * FROM transactions WHERE account_id = ?', (id,))
    transactions = cursor.fetchall()
    print("\nTransactions:")
    for transaction in transactions:
        print(f"Transaction ID: {transaction[0]}, Account ID: {transaction[1]}, Amount: {transaction[2]}, Type: {transaction[3]}, Timestamp: {transaction[4]}")

def delete_account(id):
    cursor.execute('DELETE FROM accounts WHERE id = ?', (id,))
    cursor.execute('DELETE FROM transactions WHERE account_id = ?', (id,))
    conn.commit()
    print(f"\nAccount with ID {id} deleted successfully!")

def clear_database():
    cursor.execute('DELETE FROM accounts')
    cursor.execute('DELETE FROM transactions')
    conn.commit()
    print("\nDatabase cleared successfully!")
    
def main():
    while True:
        print("\nBanking System Menu:")
        print("1. Create Account")
        print("2. Get Account Details")
        print("3. Get All Accounts")
        print("4. Withdraw Money")
        print("5. Deposit Money")
        print("6. Delete Account")
        print("7. Clear Database")
        print("8. Show Transactions")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter account name: ")
            balance = float(input("Enter initial balance: "))
            create_account(name, balance)
        elif choice == '2':
            id = int(input("Enter account ID: "))
            get_account(id)
        elif choice == '3':
            get_all_accounts()
        elif choice == '4':
            id = int(input("Enter account ID: "))
            amount = float(input("Enter withdrawal amount: "))
            withdraw_money(id, amount)
        elif choice == '5':
            id = int(input("Enter account ID: "))
            amount = float(input("Enter deposit amount: "))
            deposit_money(id, amount)
        elif choice == '6':
            id = int(input("Enter account ID to delete: "))
            delete_account(id)
        elif choice == '7':
            clear_database()
        elif choice == '8':
            id = int(input("Enter account ID to show transactions: "))
            show_transactions(id)
        elif choice == '9':
            print("\nExiting the program.")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()