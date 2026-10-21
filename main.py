
import json

monthly_budget = 5000.0

# Load previously saved transactions.
try:
    with open("expenses.json", "r") as file:
        expenses = json.load(file)
except FileNotFoundError:
    expenses = []

while True:
    print("\n--- CampusSpend ---")

    category = input("Enter expense category: ").strip().title()

    if not category:
        print("Category cannot be empty.")
        continue

    try:
        amount = float(input("Enter expense amount (₹): "))

        if amount <= 0:
            print("Expense must be greater than zero.")
            continue

    except ValueError:
        print("Please enter a valid number.")
        continue

    expense = {
        "category": category,
        "amount": amount
    }
    expenses.append(expense)

    # Save all transactions to the JSON file.
    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=4)

    choice = input("Add another expense? (yes/no): ").strip().lower()

    while choice not in ("yes", "no"):
        choice = input("Please enter yes or no: ").strip().lower()

    if choice == "no":
        break

total_expenses = sum(expense["amount"] for expense in expenses)
remaining_budget = monthly_budget - total_expenses

print("\n===== CampusSpend Summary =====")
print(f"Monthly budget:   ₹{monthly_budget:.2f}")
print(f"Total expenses:   ₹{total_expenses:.2f}")
print(f"Remaining budget: ₹{remaining_budget:.2f}")

print("\n===== Transaction History =====")

for number, expense in enumerate(expenses, start=1):
    print(f"{number}. {expense['category']}: ₹{expense['amount']:.2f}")

if remaining_budget < 0:
    print("\nWarning: You have exceeded your budget!")
else:
    print("\nYou are within your budget!")
