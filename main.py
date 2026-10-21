monthly_budget=5000
total_expenses=0
continue_tracking="yes"
while continue_tracking=="yes":
 expense_category=input("Enter expense category:")
 expense_amount=float(input(f"Enter your {expense_category} expense: "))
 total_expenses=total_expenses+expense_amount
 continue_tracking = input("Add another expense? (yes/no): ")

remaining_budget = monthly_budget - total_expenses

print("Monthly budget:", monthly_budget)
print("Total expenses:", total_expenses)
print("Remaining budget:", remaining_budget)

if remaining_budget >= 0:
    print("You are within your budget")
else:
    print("You have exceeded your budget")