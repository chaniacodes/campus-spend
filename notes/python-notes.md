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