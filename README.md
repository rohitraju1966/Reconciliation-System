# Data Reconciliation Script

## Overview
This Python script performs data reconciliation between two unordered datasets (Company Data and Government Data). It matches rows based on GST numbers and compares invoice numbers (and other fields) using a character-level similarity metric provided by the `fastwer` library. The script then produces an output Excel file containing:

- Processed company data.
- Reordered government data matched to the company rows.
- A reconciliation sheet that indicates, for each field, whether the data is **"RECONCILED"** or shows a **"MISMATCH ERROR"**.

## Prerequisites
Before running the script, please ensure the following:

### Data Format:
The data in both CSV files must be arranged such that:
- The first row contains the column names (with no merged cells).
- The following rows contain the actual data.

### Known Column Names:
- The GST number and invoice number column names for both datasets must be known.

### Data Types:
- Ensure that the data types of columns remain consistent across the datasets (preferably using floats for numeric fields and strings for all others).

### Required Libraries:
Install the following prerequisite libraries:
```bash
pip install pybind11
pip install fastwer
```

## Installation
1. Clone or download this repository.
2. Ensure you have Python 3.x installed.
3. Install the required libraries using pip as shown above.

## Data Requirements
### Company Data CSV:
Contains columns such as `Invoice No`, `GST No`, `Supplier Name`, etc.

### Government Data CSV:
Contains corresponding columns such as `Invoice number`, `GSTIN of supplier`, etc.

Update the file paths in the script for the variables `df` and `df_1` to point to your CSV files.

## Usage
### Update CSV Paths:
Edit the lines where the CSV files are read:
```python
import pandas as pd

df = pd.read_csv("path_to_company_data.csv")   # INSERT THE LINK TO COMPANY DATA as CSV file
df_1 = pd.read_csv("path_to_govt_data.csv")   # INSERT THE LINK TO GOVT DATA as CSV file
```

### Adjust Column Names and Fields:
When calling the `rows_columns_match()` function, make sure that you specify the correct column names for invoice and GST numbers, as well as the list of columns to reconcile. For example:
```python
df_3, df_4, df_5 = rows_columns_match(
    df, df_1,
    'Invoice No', 'Invoice number',
    'GST No', 'GSTIN of supplier',
    ['Supplier Name', 'Invoice No', 'Invoice Date', 'Basic Amt', 'SGST', 'CGST', 'IGST', 'GST No']
)
```

### Run the Script:
Execute the script. The results will be written to an Excel file named `DATA_outputs.xlsx` containing three sheets:

- **Company_data**: Processed company data.
- **govt_data_new**: Reordered government data matched to company rows.
- **reconciliation_sheet**: A field-by-field reconciliation status.

## Code Explanation
### 1. Data Preprocessing:
- Reads the CSV files.
- Fills missing values with `0`.
- Filters the company data to only include the columns specified by the user.

### 2. Row Matching (First Pass):
- A subset of company rows (1/8th of the data if the dataset is large) is used to match invoice numbers between the datasets, considering only rows where the GST numbers match.
- The `fastwer.score_sent` function is used to calculate similarity between invoice numbers.

### 3. Column Mapping:
- The script compares average similarity scores between the company columns and government columns (from the sample) to determine the best matching columns.
- The government dataset columns are then rearranged to match the company dataset.

### 4. Row Matching (Second Pass):
- For each row in the company dataset, the script concatenates all cell values into a single string and finds the best-matching row from the government data (again, only matching rows with identical GST numbers).

### 5. Reconciliation:
- A reconciliation dataframe is created by comparing each field between the matched company and government rows.
- Each field is labeled as **"RECONCILED"** if the data matches or **"MISMATCH ERROR"** if it does not.

### 6. Output:
- The final outputs are written to an Excel file with three sheets for further review.

## Limitations
### 1. Performance:
- The script uses nested loops and the deprecated `DataFrame.append()` method.
- While acceptable for a proof-of-concept and small datasets, you may need to optimize these parts for larger datasets or production use.

### 2. Robustness:
- The approach of concatenating all cell values into a string for matching may be sensitive to formatting differences.
- Further error handling and data normalization might be required for a production system.

## License
This project is provided "as-is" for proof-of-concept purposes. Use and modify the code at your own risk.

## Contact
For any questions, suggestions, or improvements, please feel free to contact **[Your Name]** or open an issue in the repository.
