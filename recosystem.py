'''
Few points to consider before running the code:
1. The data must be arranged in the following format for both company and govt dataset 
   1. Only the first row must contain the column names (no cells must be merged)
   2. The following rows must contain intended data 
2. GST number, invoice number column names of both the govt and company data must be known
3. Please make sure that the datatype of the columns remain the same, if possible follow float for all the numeric columns and string for the rest
4. Please install two prerequisite libraries once to the server 
   1. use the following code to install:
      !pip install pybind11
      !pip install fastwer
'''

# Install required libraries
!pip install pybind11
!pip install fastwer

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import Image, display
from sklearn import preprocessing
from scipy import spatial
import fastwer
from sklearn.preprocessing import LabelEncoder

# Read the CSV files for company and government data.
# (Provide the proper file paths/links inside the quotes.)
df = pd.read_csv("")   # INSERT THE LINK TO COMPANY DATA as CSV file
df_1 = pd.read_csv("") # INSERT THE LINK TO GOVT DATA as CSV file

def rows_columns_match(df, df_1, Invoice_no, Invoice_number, GST_no, GST_number, ar):
    """
    This function attempts to reconcile two unordered datasets (company and govt)
    by matching rows based on GST numbers and comparing invoice numbers (and other columns)
    using a character-level similarity metric (fastwer.score_sent).

    Parameters:
      df           : Company dataframe.
      df_1         : Government dataframe.
      Invoice_no   : Column name for invoice number in the company dataframe.
      Invoice_number: Column name for invoice number in the government dataframe.
      GST_no       : Column name for GST number in the company dataframe.
      GST_number   : Column name for GST number in the government dataframe.
      ar           : List of columns to be reconciled (must be present in both datasets).

    Returns:
      df   : Processed company dataframe (filtered to columns in 'ar').
      df_3 : Reordered government dataframe rows (matched to company rows).
      df_4 : Reconciliation dataframe showing 'RECONCILED' or 'MISMATCH ERROR' for each field.
    """

    # Fill missing values with 0 in the company dataframe and restrict to the desired columns.
    df = df.fillna(0)
    df = df[ar]

    # Fill missing values with 0 in the government dataframe.
    df_1 = df_1.fillna(0)

    # Create an empty dataframe (df_2) with the same columns as the government data.
    df_2 = pd.DataFrame(columns=df_1.columns)
    
    # Set an initial large value to compare similarity scores.
    result = 10**10

    # Determine the number of rows to process:
    # If the company dataset is large (>500 rows), use about 1/8th of the rows.
    if len(df) > 500:
        s = int(len(df) / 8)
    else:
        s = len(df)
    
    # -------------------------------
    # First Pass: Match a subset of rows based on invoice number similarity for rows with matching GST.
    # -------------------------------
    for i in range(s):
        y = -1           # Will hold the index of the best matching row from the govt data.
        result1 = result # Reset the best (minimum) score for this iteration.
        
        # Iterate through each row in the government dataset (using the invoice number column).
        for j in range(len(df_1[Invoice_number])):
            # Convert invoice numbers to strings for comparison.
            k = str(df[Invoice_no][i])
            k1 = str(df_1[Invoice_number][j])
            
            # Only consider rows where the GST numbers match exactly.
            if df[GST_no][i] == df_1[GST_number][j]:
                # Compute the similarity score between the two invoice numbers.
                result = fastwer.score_sent(k, k1, char_level=True)
                # Update the best match if a lower score (better match) is found.
                if result < result1:
                    result1 = result
                    y = j
                    # If a perfect match is found, exit the inner loop early.
                    if result == 0:
                        break
        # Append the best matching government row to df_2;
        # if no match was found (y remains -1), append an empty row.
        if y == -1:
            df_2 = df_2.append(pd.Series(), ignore_index=True)
        else:
            df_2 = df_2.append(df_1.iloc[y], ignore_index=True)
    
    # -------------------------------
    # Second Pass: Match columns by comparing average similarity scores.
    # For each column in the company data, determine which govt column it matches best.
    # -------------------------------
    arr = []
    for col_company in df.columns:
        arr_1 = []  # List to hold average scores for each govt column.
        for col_govt in df_2.columns:
            arr_2 = []  # List to hold similarity scores for each row.
            for k in range(len(df_2)):
                score = fastwer.score_sent(str(df[col_company][k]), str(df_2[col_govt][k]), char_level=True)
                arr_2.append(score)
            # Compute the average score for this column pair.
            arr_1.append(np.average(arr_2))
        # Choose the govt column with the lowest average score as the matching column.
        arr.append(df_2.columns[arr_1.index(min(arr_1))])
    
    # Rearrange the govt dataframe columns to match the company dataframe's column order.
    df_1 = df_1[arr]
    
    # -------------------------------
    # Prepare for row-level matching: 
    # Create a temporary 'added' column in both dataframes by concatenating all cell values in a row.
    # This will be used to compare overall row similarity.
    # -------------------------------
    df['added'] = [0] * len(df)
    df_1['added'] = [0] * len(df_1)
    
    # Rename govt dataframe columns to be identical to company dataframe columns for easier comparison.
    df_1.set_axis(df.columns, axis=1, inplace=True)
    
    # Create an empty dataframe (df_3) with the same columns as df_1 to store the best matching govt rows.
    df_3 = pd.DataFrame(columns=df_1.columns)
    
    # Create a reconciliation dataframe (df_4) with the same number of rows as company data.
    df_4 = pd.DataFrame(0, index=np.arange(len(df)), columns=ar)
    
    # Concatenate all column values into a single string for each row in the company dataframe.
    for i in range(len(df)):
        s = ''
        for col in df.columns:
            s += str(df[col][i])
        df.at[i, 'added'] = s  # Use .at to set the value for a particular cell.
    
    # Do the same for the government dataframe.
    for i in range(len(df_1)):
        s1 = ''
        for col in df_1.columns:
            s1 += str(df_1[col][i])
        df_1.at[i, 'added'] = s1
    
    # -------------------------------
    # Second Pass: Reorder govt rows to best match the company rows.
    # -------------------------------
    GST_number = GST_no  # Alias for clarity.
    for i in range(len(df['added'])):
        result = 10**10
        y = -1  # Will hold the index of the best matching govt row.
        result1 = result
        
        for j in range(len(df_1['added'])):
            k = df['added'][i]
            k1 = df_1['added'][j]
            # Only compare rows with matching GST numbers.
            if df[GST_no][i] == df_1[GST_number][j]:
                score = fastwer.score_sent(k, k1, char_level=True)
                if score < result1:
                    result1 = score
                    y = j
                    if score == 0:
                        break
        # Append the best matching row from govt data to df_3;
        # if no match is found, append an empty row.
        if y == -1:
            df_3 = df_3.append(pd.Series(), ignore_index=True)
        else:
            df_3 = df_3.append(df_1.iloc[y], ignore_index=True)
    
    # Remove the temporary 'added' column from both dataframes.
    df.drop(['added'], axis=1, inplace=True)
    df_3.drop(['added'], axis=1, inplace=True)
    
    # -------------------------------
    # Final Step: Reconcile the two datasets field by field.
    # -------------------------------
    # Re-create the reconciliation dataframe to store the status for each column.
    df_4 = pd.DataFrame(0, index=np.arange(len(df)), columns=ar)
    for i in range(len(df)):
        for col in ar:
            if df[col][i] == df_3[col][i]:
                df_4.at[i, col] = 'RECONCILED'
            else:
                df_4.at[i, col] = 'MISMATCH ERROR'
    
    # Write the results to an Excel file with three sheets:
    # 1. Company data, 2. Reordered govt data, 3. Reconciliation results.
    with pd.ExcelWriter('DATA_outputs.xlsx') as writer:
        df.to_excel(writer, sheet_name='Company_data')
        df_3.to_excel(writer, sheet_name='govt_data_new')
        df_4.to_excel(writer, sheet_name='reconciliation_sheet')
    
    '''
    # Alternatively, to save the sheets as separate Excel files, uncomment the code below:
    writer = pd.ExcelWriter('reconciliation_sheet.xlsx')
    df_4.to_excel(writer)
    writer.save()

    writer1 = pd.ExcelWriter('Company_data.xlsx')
    df.to_excel(writer1)
    writer1.save()

    writer2 = pd.ExcelWriter('govt_data_new.xlsx')
    df_3.to_excel(writer2)
    writer2.save()
    '''
    
    return df, df_3, df_4

# ------------------------------------------------------------------
# Example usage:
# Call the function with appropriate column names and the list of columns to reconcile.
# Adjust these parameters based on your specific datasets.
# ------------------------------------------------------------------
df_3, df_4, df_5 = rows_columns_match(df, df_1, 'Invoice No', 'Invoice number', 'GST No', 'GSTIN of supplier', ['Supplier Name', 'Invoice No', 'Invoice Date', 'Basic Amt', 'SGST', 'CGST', 'IGST', 'GST No'])

# The returned dataframes are:
df_3  # Processed company data (filtered to the columns in 'ar')
df_4  # Reordered govt data matched to company rows
df_5  # Reconciliation sheet indicating match status for each field
