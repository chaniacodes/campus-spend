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