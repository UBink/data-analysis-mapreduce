#!/usr/bin/env python3
import sys

current_key = None
temp_sum = 0
count = 0
max_temp = -float('inf')
min_temp = float('inf')

# Process the key-value pairs
for line in sys.stdin:
    try:
        line = line.strip()
        key, value = line.split("\t")

        # Parse the key - expecting station,year,season
        key_parts = key.split(",")
        if len(key_parts) != 3:
            # If not 3 parts, log warning and try to handle it
            sys.stderr.write(f"WARNING: Key has {len(key_parts)} parts instead of 3: {key}\n")
            continue
        else:
            station, year, season = key_parts

        # Parse the temperature value
        temp = float(value)

        # Create a tuple key that includes year
        full_key = (station, year, season)

        # Aggregate sum of temperatures, count occurrences, and track max/min temperatures
        if current_key == full_key:
            temp_sum += temp
            count += 1
            max_temp = max(max_temp, temp)
            min_temp = min(min_temp, temp)
        else:
            if current_key:
                # Output average, max, and min temperatures for the previous key
                avg_temp = temp_sum / count
                print(f"{current_key[0]},{current_key[1]},{current_key[2]}\tAverage: {avg_temp:.2f}, Max: {max_temp:.2f}, Min: {min_temp:.2f}")
            
            # Reset the variables for the new key
            current_key = full_key
            temp_sum = temp
            count = 1
            max_temp = temp
            min_temp = temp

    except Exception as e:
        # For debugging - log problematic lines
        sys.stderr.write(f"ERROR processing line: {line} - {str(e)}\n")
        continue

# Output the last key-value pair
if current_key:
    avg_temp = temp_sum / count
    print(f"{current_key[0]},{current_key[1]},{current_key[2]}\tAverage: {avg_temp:.2f}, Max: {max_temp:.2f}, Min: {min_temp:.2f}")