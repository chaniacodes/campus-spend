# Python Learning Notes

## Lists

A list stores multiple items in a single variable.

Example:

`expenses = []`

This creates an empty list.

## The append() Method

`list.append(item)` adds an item to the end of a list.

Example:

`expenses.append(120)`

If the list was empty, it now contains `[120]`.

## Why CampusSpend Uses Lists

Instead of remembering only the total amount spent, CampusSpend can store each expense separately. This will let us display individual transactions and analyse spending later.

**Remember:** `append()` adds an item to the list. It does not calculate the total automatically.

## File Handling and JSON

- `open(file, "r")`: Opens a file for reading.
- `open(file, "w")`: Opens a file for writing, replacing existing contents.
- `with open(...) as file`: Manages the file's lifecycle and closes it automatically.
- `json.load(file)`: Reads JSON from a file and converts it to Python objects.
- `json.dump(data, file, indent=4)`: Writes Python data as formatted JSON.
- `FileNotFoundError`: An exception raised when the requested file does not exist.

### Why CampusSpend Uses JSON

Without persistence, expenses disappear when the program closes. JSON lets CampusSpend save transactions and load them during the next run.

**Important:** Write mode (`"w"`) replaces the file's existing contents. In this project, we first load the existing list, append the new transaction, and then save the complete list.

## Dates in Python

- `from datetime import date` imports date utilities.
- `date.today()` returns today's date.
- `.isoformat()` converts a date to `YYYY-MM-DD`.
- `.strftime("%Y-%m")` formats a date as year and month.
- `datetime.strptime(value, "%Y-%m")` validates a year-month input.
- `startswith()` checks whether a string begins with a given value.
- List comprehensions can filter transactions based on a condition.

## Dictionaries and Category Analytics

- Dictionaries store key-value pairs.
- `dict.get(key, default)` returns a value or a default if the key is missing.
- A loop can aggregate multiple transactions into category totals.
- `sorted()` can sort dictionary items using a custom key.
- Percentage = (category amount / total spending) * 100.

## Unit Testing in Python

### What is unit testing?
Unit testing means testing individual parts of a program automatically to check whether they behave as expected.

Python has a built-in testing framework called `unittest`, so we don't need to install an extra package.

### Important concepts
- **Test case:** A test that checks a particular behavior.
- **Assertion:** A check that compares the actual result with the expected result.
- `self.assertEqual(actual, expected)`: Checks whether two values are equal.
- `self.assertTrue(condition)`: Checks whether a condition is true.
- `setUp()`: Prepares test data before each test runs.
- `unittest.main()`: Runs the tests when the test file is executed directly.

### Our CampusSpend tests
We created `tests/test_main.py` to test:
1. Whether monthly filtering returns the correct transactions.
2. Whether transactions from other months are excluded.
3. Whether a month with no transactions returns an empty list.
4. Whether the monthly budget is ₹5,000.

### How to run the tests
From the project's root folder, run:

```bash
py -m unittest discover -s tests -v
```

- `py -m unittest`: Runs Python's testing framework.
- `discover`: Automatically finds test files.
- `-s tests`: Looks inside the `tests` folder.
- `-v`: Displays each test name and its result.

**Successful output:** `Ran 4 tests` followed by `OK`.

### Why testing matters
Automated tests help us catch bugs when we change existing code. We can rerun them after

## Testing File Storage in Python

### 1. Saving and loading JSON data
- `save_expenses(expenses)` writes transaction data to a JSON file.
- `load_expenses()` reads saved transactions back into Python.
- `json.dump()` converts Python data into JSON and writes it to a file.
- `json.load()` reads JSON data and converts it back into Python objects.

### 2. Temporary files
`tempfile.TemporaryDirectory()` creates a temporary folder for testing. Python automatically cleans it up when the block finishes.

We use temporary files so automated tests don't accidentally change our real expense data.

### 3. Mocking with patch
`patch.object(main, "DATA_FILE", test_file)` temporarily changes the file path used by our program.

During the test, CampusSpend uses the temporary test file instead of the real `expenses.json`.

### 4. New tests in CampusSpend
- `test_save_and_load_expenses`: checks that saved transactions can be loaded correctly.
- `test_load_expenses_returns_empty_list_when_file_missing`: checks that loading returns an empty list if the file doesn't exist.

### 5. Why these tests matter
File storage is essential for an expense tracker. These tests help verify that transactions persist correctly and that a first-time user can run the application without an existing data file.

### Current test coverage
CampusSpend currently has 9 unit tests covering monthly filtering, the budget constant, invalid expense inputs, and JSON file storage.

## Handling Legacy Data Safely

### What is legacy data?
Legacy data is information saved by an older version of a program. When we add new features, older records may not contain the fields our updated program expects.

### The problem in CampusSpend
Earlier versions of CampusSpend saved expenses without a date. Assigning today's date to those transactions could make monthly spending reports inaccurate.

### Our solution
- `expense.get("date")` safely retrieves a date when available.
- Missing dates are represented by `None`, meaning the date is unknown.
- `get_month_expenses()` excludes transactions without a known date.
- Transaction history displays `Unknown date` instead of inventing a date.
- The application no longer automatically rewrites the entire data file at startup.

### Data validation
When loading JSON records, we check that:
- The overall data is a list.
- Each transaction is a dictionary.
- The category is a string.
- The amount is a positive number.
- A supplied date follows the `YYYY-MM-DD` format.

Invalid records should not silently produce misleading reports.

### Regression testing
A regression test checks that a new code change doesn't break existing behavior. Our legacy-data test verifies that an expense without a date retains its amount and receives `None` as its date rather than today's date.

##  Modules and Separation of Concerns

A **module** is a Python file containing reusable code, such as functions and variables. We can import code from one module into another.

Example:
```python
from storage import load_expenses, save_expenses
```

This imports two functions from `storage.py`.

### Separation of Concerns

Separation of concerns means giving different parts of a program different responsibilities.

In CampusSpend:
- `main.py` handles the menu and user interaction.
- `storage.py` handles reading and writing expense data.
- `expense_logic.py` handles expense filtering and calculations.
- `tests/` checks whether the program behaves correctly.

This makes code easier to understand, test, debug, and maintain.

### Return Values vs. Printing

`print()` displays information to the user, while `return` sends a result back to the code that called the function.

For example:
```python
def add_numbers(a, b):
    return a + b

result = add_numbers(10, 20)
print(result)
```

The function returns `30`, which can be stored, tested, or used in further calculations.

### Unit Testing

A unit test checks a small part of a program independently.

```python
self.assertEqual(actual, expected)
```

This checks whether the actual result matches the expected result.

A failing test may indicate a code bug or an incorrect expected value. Always compare the expected result against the input data before changing the implementation.

## Safer File Storage and Atomic Replacement

When saving important data, writing directly to the original file can be risky. If a write fails midway, the file may become incomplete.

### Temporary-file approach

1. Write the updated data to a temporary file.
2. Flush buffered data and close the file.
3. Replace the original file only after writing succeeds.
4. Clean up the temporary file if saving fails.

### Important Python concepts

- `Path.with_name()` creates a new path with a different filename in the same directory.
- `file.flush()` pushes buffered data toward the operating system.
- `os.fsync(file.fileno())` requests that the operating system flush file data to storage.
- `Path.replace()` replaces the destination path with the new file.
- `raise` propagates an exception to the caller.
- `unittest.mock.patch()` can simulate failures without actually damaging files.

### Failure testing

A good test suite checks both successful operations and failure scenarios.

For CampusSpend, the failed-replacement test verifies that the original expense data remains intact when replacing the file raises an `OSError`.

Atomic replacement reduces the risk of partial writes, but it is not a substitute for backups and does not guarantee protection against every hardware or filesystem failure.

## Editing and Deleting Expenses

### Accessing List Items by Index

A list stores items in order, and each item has an index starting at `0`.

```python
expenses = ["Food", "Transport", "Books"]

print(expenses[0])  # Food
print(expenses[1])  # Transport
```

If a user selects transaction number `1`, we convert it to index `0`:

```python
index = choice - 1
```

This is necessary because menu numbering starts at `1`, while Python list indexing starts at `0`.

### Copying Dictionaries

An expense is stored as a dictionary. The `copy()` method creates a separate, shallow copy of that dictionary.

```python
original_expense = expenses[index].copy()
updated_expense = original_expense.copy()
```

We edit `updated_expense` while keeping `original_expense` unchanged. If saving fails, the original data can be restored.

### Removing and Restoring List Items

`pop(index)` removes an item and returns it.

```python
deleted_expense = expenses.pop(index)
```

If saving fails, `insert(index, item)` restores the transaction at its original position:

```python
expenses.insert(index, deleted_expense)
```

This helps prevent accidental data loss when a deletion cannot be saved.

### Input Validation

User input from `input()` is always returned as a string.

```python
amount_input = input("Enter amount: ").strip()
```

We convert it to a number and catch invalid input:

```python
try:
    amount = float(amount_input)

    if amount <= 0:
        print("Amount must be positive.")

except ValueError:
    print("Enter a valid numeric amount.")
```

`.strip()` removes whitespace at the beginning and end of a string. Empty input can also be used to mean "keep the current value" when editing.

### Exception Handling and Rollback

Saving a file may raise an `OSError`. In edit and delete operations, we catch the error and restore the original in-memory transaction.

This is a simple form of rollback: undoing an in-memory change when the operation cannot be completed successfully.

### Mocking in Unit Tests

`unittest.mock.patch()` lets tests replace real behaviour with controlled behaviour.

For example:

```python
with patch("builtins.input", side_effect=["1", "", "200"]):
    edit_expense(expenses)
```

This simulates selecting transaction 1, keeping its category unchanged, and entering an amount of 200.

We can also simulate a storage failure:

```python
with patch.object(
    main,
    "save_expenses",
    side_effect=OSError("Simulated save failure"),
):
    edit_expense(expenses)
```

This allows us to test error handling without deliberately damaging files.

### Testing Important Scenarios

For every feature, test more than the successful case.

For editing and deleting, useful scenarios include:

- Updating a transaction successfully.
- Rejecting invalid amounts.
- Cancelling a deletion.
- Restoring an original transaction when saving fails.
- Rejecting invalid transaction numbers.
- Handling an empty expense list.

##  UUIDs, Persistent IDs, and Data Migration

### 1. What is a UUID?

**UUID** stands for *Universally Unique Identifier*. It is an identifier used to distinguish one record from another.

In CampusSpend, every expense needs its own ID so we can edit or delete the correct transaction, even if multiple expenses have the same category and amount.

```python
import uuid

expense_id = uuid.uuid4().hex
print(expense_id)
```

- `uuid` is Python's built-in module for generating UUIDs.
- `uuid.uuid4()` generates a random UUID.
- `.hex` represents the UUID as a hexadecimal string without hyphens.

Example output:

```text
a1b2c3d4e5f6478890abcdef12345678
```

The output will be different each time.

### 2. Adding an ID to an expense

When a new expense is created, generate its ID and store it with the other information.

```python
expense = {
    "id": uuid.uuid4().hex,
    "category": "Food",
    "amount": 150.0,
    "date": "2026-10-22"
}
```

Each expense now has four fields: `id`, `category`, `amount`, and `date`.

**Why use an ID instead of the category or amount?**

Two expenses can have the same category, amount, and date. A unique ID lets us distinguish them reliably.

### 3. What is data migration?

**Data migration** means updating existing saved data to work with a newer version of an application.

Suppose an older version of CampusSpend saved expenses like this:

```python
{
    "category": "Food",
    "amount": 100.0,
    "date": "2026-10-22"
}
```

The newer version expects every expense to have an ID. We must update older records that don't have one.

```python
if "id" not in expense:
    expense["id"] = uuid.uuid4().hex
    migrated = True
```

- `"id" not in expense` checks whether the record lacks an ID.
- A new ID is generated only when the ID is missing.
- `migrated = True` records that the data was changed.

### 4. Why do we use a migration flag?

A migration flag helps us determine whether the saved data needs updating.

```python
migrated = False

# Check and update old records here.

if migrated:
    save_expenses(expenses)
```

Initially, `migrated` is `False`.

If any record needs updating, it becomes `True`. We then save the updated records to the JSON file.

This avoids unnecessarily rewriting the file every time the application starts.

### 5. What are persistent IDs?

A **persistent ID** remains the same after the application closes and restarts.

Our application:
1. Loads the expenses from the JSON file.
2. Generates IDs for older records that don't have them.
3. Saves the updated records.
4. Loads the same IDs on subsequent runs.

This is important because generating a new ID every time an expense is loaded would make its identity unstable.

### 6. How we tested ID migration

Our test, `test_legacy_expense_receives_persistent_id`, checks that:

- An old expense without an ID receives one.
- The generated ID is not empty.
- Loading the file again preserves the same ID.
- The expense's existing category remains unchanged.

**Key testing concept:** A good test checks both that a new feature works and that existing data is preserved.

### Quick revision

| Concept | Meaning |
|---|---|
| UUID | An identifier designed to be unique |
| `uuid.uuid4().hex` | Generates a random UUID as a hexadecimal string |
| Data migration | Updating older saved data for a newer application version |
| Persistent ID | An ID that stays the same across application restarts |
| Migration flag | Tracks whether saved data has been changed |
| Regression testing | Checking that existing functionality still works after changes |

## Filtering Data in Python

### 1. What is filtering?

Filtering means selecting only the items that satisfy a particular condition from a collection.

For example, from a list of expenses, we can select only Food expenses or transactions within a particular date range.

### 2. Optional parameters

```python
def filter_expenses(expenses, category=None):
```

`category=None` makes the category filter optional. If no category is provided, the function can return expenses from all categories.

### 3. The `continue` statement

```python
if category and expense["category"].lower() != category.lower():
    continue
```

`continue` skips the current loop iteration and moves to the next item.

Here, expenses whose categories don't match are skipped.

Using `.lower()` makes the comparison case-insensitive, so `"Food"` and `"food"` match.

### 4. Date filtering

Our expenses use the `YYYY-MM-DD` date format.

```python
if start_date and expense_date < start_date:
    continue
```

This skips expenses that occurred before the selected start date.

Similarly, comparing against `end_date` excludes expenses after the selected end date. Both boundaries are inclusive.

ISO-formatted dates can be compared as strings chronologically, provided they are valid and consistently formatted.

### 5. Input validation

```python
datetime.strptime(date_value, "%Y-%m-%d")
```

This checks whether a date matches the expected format and represents a valid calendar date. Invalid values raise `ValueError`, which we handle to prevent the application from crashing.

We also check that the start date isn't later than the end date.

### 6. Combining filters

Users can apply multiple filters together. For example, category `Food` and October's date range return only Food expenses recorded during October.

### 7. Separation of concerns

- `expense_logic.py` contains the filtering logic.
- `main.py` handles user input and displays the results.
- `tests/` checks that the functionality behaves correctly.

Keeping these responsibilities separate makes the application easier to test, maintain, and extend.

## Configurable Budgets in CampusSpend

### 1. Why make budgets configurable?

A hard-coded budget is fixed in the source code. A configurable budget lets the user choose their own monthly spending limit and category-specific limits.

In CampusSpend, budget settings are stored separately from expense transactions in `budgets.json`.

This keeps two kinds of data separate:
- `expenses.json` stores transaction records.
- `budgets.json` stores the user's budget settings.

### 2. Monthly and category budgets

A monthly budget limits total spending for a selected month. A category budget limits spending within a particular category.

For example:
- Monthly budget: ₹5,000
- Food budget: ₹2,000
- Transport budget: ₹800

A category can exceed its individual budget even when total monthly spending remains within the monthly limit.

### 3. Calculating budget status

For each budget, we calculate:

- **Remaining:** Budget − Amount spent
- **Overspending:** The amount spent beyond the budget, or zero if the budget has not been exceeded.

Example:

```python
budget = 2000
spent = 2300

remaining = budget - spent
over_budget = max(0, spent - budget)
```

Here, `remaining` is `-300` and `over_budget` is `300`.

The negative remaining amount indicates that spending exceeded the limit. `max(0, ...)` prevents the overspending value from becoming negative.

### 4. Using `.setdefault()`

```python
category_budgets = settings["category_budgets"].setdefault(month, {})
```

`setdefault(key, default)` returns the existing value for a dictionary key. If the key does not exist, it creates the key with the supplied default value.

Here, it ensures that the selected month has a category-budget dictionary before category budgets are added.

---

## Spending Analytics for CampusSpend Wrapped

### 1. Calculating budget usage percentage

A percentage makes it easier to understand how much of a budget has been used.

Formula:

**Budget usage (%) = (Amount spent ÷ Budget) × 100**

```python
def calculate_budget_percentage(total_spent, budget):
    if budget <= 0:
        return 0.0
    return (total_spent / budget) * 100
```

For a budget of ₹5,000 and spending of ₹2,500, the result is `50.0`, meaning 50% of the budget has been used.

The function returns `0.0` when the budget is zero or negative, avoiding division by zero and an undefined percentage.

### 2. Finding the top-spending category

The top-spending category is the category with the greatest total spending during a selected month.

```python
top_category = max(category_totals, key=category_totals.get)
```

- `max()` finds the item with the greatest value.
- `key=category_totals.get` tells Python to compare categories using their spending totals.

We first check whether the dictionary contains any categories. If it is empty, there is no top category to report.

CampusSpend returns `(None, 0.0)` when there are no expenses for the month. This prevents the application from reporting a made-up category.

### 3. Combining calculations into a monthly recap

A monthly recap combines several calculations into one result.

For example, `generate_monthly_wrapped()` can gather:

- Selected month
- Total amount spent
- Highest-spending category and its total
- Percentage of the monthly budget used
- Spending totals for each category

The function returns these values in a dictionary. Other parts of the application can then display the information without repeating the calculations.

This follows separation of concerns: calculation functions determine the results, while the user interface decides how to present them.

### 4. Why return a dictionary?

A dictionary gives each result a meaningful key.

```python
summary = {
    "total_spent": 2500.0,
    "top_category": "Food",
    "budget_percentage": 50.0
}
```

The values can be accessed by key:

```python
print(summary["total_spent"])
```

This is useful when the recap contains several related results, especially when we later build a visual interface.

### 5. Testing analytics functions

Analytics functions should be tested with different scenarios:

- A month with several expenses
- A month with no expenses
- A category that has the highest total
- A budget with zero or a negative value
- Spending below, equal to, and above the budget

Tests should verify the returned values rather than only checking what appears on screen. This makes the calculations easier to test independently of the interface.

**Important:** A spending recap must be based on the user's actual saved transactions. If sample data is used during development, it should be identified as sample data rather than presented as the user's spending history.

## Annual Wrapped and Grouping Transactions by Year

### 1. Filtering transactions by year

CampusSpend Annual Wrapped analyses expenses recorded during a selected year.

```python
expense["date"].startswith(year + "-")
```

For example, when `year = "2026"`, this matches dates beginning with `"2026-"`, such as `"2026-10-22"`.

The hyphen matters because it distinguishes the year prefix from other possible strings. Transactions with unknown dates (`None`) must be excluded before calling `startswith()`.

### 2. Grouping spending by month

Annual Wrapped needs to calculate the total spent in each month.

```python
month = expense["date"][:7]
```

For a date like `"2026-10-22"`, slicing with `[:7]` extracts `"2026-10"`.

We use this month value as a dictionary key and add each transaction's amount to its monthly total. This is called **aggregation**: combining individual records into summary values.

### 3. Finding the highest-spending month

Once monthly totals have been calculated, we can identify the month with the largest total.

```python
highest_month = max(monthly_totals, key=monthly_totals.get)
```

The result is the month key, not the amount spent. We retrieve its corresponding amount separately:

```python
highest_month_amount = monthly_totals[highest_month]
```

We must check that `monthly_totals` is not empty before using `max()`, because calling `max()` on an empty dictionary raises `ValueError`.

### 4. Calculating average monthly spending

In CampusSpend Annual Wrapped, the average is calculated across months that contain recorded expenses.

**Average spending = Total yearly spending ÷ Number of months with recorded expenses**

For example, if total spending is ₹3,600 across three months with expenses, the average is ₹1,200 per active month.

This is different from dividing by 12. Dividing by 12 would calculate the average across all calendar months, including months with no recorded transactions.

The application should make clear which average it displays.

### 5. Monthly Wrapped vs. Annual Wrapped

| Monthly Wrapped | Annual Wrapped |
|---|---|
| Filters transactions by year and month | Filters transactions by year |
| Reports total monthly spending | Reports total yearly spending |
| Identifies the top category for that month | Identifies the top category for the year |
| Calculates monthly budget usage | Compares spending across months |
| Shows category totals for one month | Shows category and monthly totals for the year |

Both features reuse the same principle: filter the relevant transactions first, then calculate summaries from the filtered data.

### 6. Handling missing data

An annual recap may have no transactions for the selected year. In this situation, it should report that no expenses were recorded instead of inventing a top category or highest-spending month.

Transactions without known dates are excluded from date-based reports because their correct year cannot be determined.

### 7. Formatting financial output

Python's formatted string syntax can display monetary values with two decimal places:

```python
print(f"Total spent: ₹{total_spent:.2f}")
```

The `:.2f` format specifier displays a number with two digits after the decimal point, making financial summaries easier to read consistently.

### Key takeaway

Annual Wrapped is built by grouping transactions at a larger time scale. Filtering determines which transactions belong in the report; aggregation calculates totals; and the recap presents those results in a useful format.

