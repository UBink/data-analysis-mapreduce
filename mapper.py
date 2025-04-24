#!/usr/bin/env python3
import sys
import pandas as pd

# Helper function to get season from month
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

# Read input from standard input
for line in sys.stdin:
    line = line.strip()
    columns = line.split(",")
    
    try:
        # Extract necessary columns
        station = columns[0]
        date = columns[1]
        
        # Skip rows with missing or invalid temperature
        temp = columns[6]  # TEMP column
        
        if temp == '*' or temp == '' or temp == '9999':
            continue
        
        # Convert to numeric
        temp = pd.to_numeric(temp, errors='coerce')
        
        # Skip invalid temperature values
        if pd.isna(temp):
            continue
        
        # Parse the date to extract month and year
        date_obj = pd.to_datetime(date)
        month = date_obj.month
        year = date_obj.year
        season = get_season(month)
        
        # Output key-value pairs for further processing
        print(f"{station},{year},{season}\t{temp}")
    except IndexError:
        continue