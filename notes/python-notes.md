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

