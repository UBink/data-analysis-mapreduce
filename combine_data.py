import os
import pandas as pd
import glob

def combine_csv_by_year(base_dir, output_dir):
    """
    Combines CSV files by year and saves them to the output directory.
    
    Args:
        base_dir (str): Base directory containing year folders with CSV files
        output_dir (str): Directory to save combined CSV files
    """
    # Ensure the paths exist
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Data directory not found: {base_dir}")
        
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Get all year directories
    year_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    if not year_dirs:
        print(f"No year directories found in {base_dir}")
        return
        
    print(f"Found year directories: {year_dirs}")
    
    for year_dir in year_dirs:
        year_path = os.path.join(base_dir, year_dir)
        csv_files = glob.glob(os.path.join(year_path, '*.csv'))
        
        if not csv_files:
            print(f"No CSV files found in {year_path}. Skipping.")
            continue
        
        print(f"Processing {len(csv_files)} CSV files from {year_dir}...")
        
        # Initialize an empty DataFrame to hold combined data
        combined_data = pd.DataFrame()
        
        # Read and combine all CSV files for the current year
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                combined_data = pd.concat([combined_data, df], ignore_index=True)
                print(f"  Added: {os.path.basename(file)}")
            except Exception as e:
                print(f"  Error processing {os.path.basename(file)}: {e}")
        
        if not combined_data.empty:
            # Save the combined data
            output_file = os.path.join(output_dir, f"{year_dir}_combined.csv")
            combined_data.to_csv(output_file, index=False)
            print(f"Saved combined data for {year_dir} to {output_file}")
            print(f"  Total rows: {len(combined_data)}")
        else:
            print(f"No valid data found for {year_dir}")

def combine_all_years(base_dir, output_dir):
    """
    Combines all CSV files across all years into a single file.
    
    Args:
        base_dir (str): Base directory containing year folders with CSV files
        output_dir (str): Directory to save combined CSV file
    """
    # First, ensure we have the combined files by year
    combine_csv_by_year(base_dir, output_dir)
    
    # Now combine all the year files into one master file
    combined_files = glob.glob(os.path.join(output_dir, '*_combined.csv'))
    
    if not combined_files:
        print("No combined files found to merge.")
        return
    
    print(f"\nCombining all {len(combined_files)} year files into one master file...")
    
    # Initialize an empty DataFrame to hold combined data
    all_data = pd.DataFrame()
    
    # Read and combine all year files
    for file in combined_files:
        try:
            df = pd.read_csv(file)
            all_data = pd.concat([all_data, df], ignore_index=True)
            print(f"  Added: {os.path.basename(file)}")
        except Exception as e:
            print(f"  Error processing {os.path.basename(file)}: {e}")
    
    if not all_data.empty:
        # Save the master combined data
        output_file = os.path.join(output_dir, "all_years_combined.csv")
        all_data.to_csv(output_file, index=False)
        print(f"Saved master combined data to {output_file}")
        print(f"  Total rows: {len(all_data)}")
    else:
        print("No valid data found to combine.")

if __name__ == "__main__":
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the data directory - adjust these paths based on your actual structure
    # If data folder is inside data-analysis-mapreduce folder:
    data_dir = os.path.join(script_dir, 'data')
    
    # If data folder is at the same level as data-analysis-mapreduce folder:
    # project_dir = os.path.dirname(script_dir)
    # data_dir = os.path.join(project_dir, 'data')
    
    # Define the output directory
    combined_dir = os.path.join(script_dir, 'combined_data')
    
    print(f"Script directory: {script_dir}")
    print(f"Data directory: {data_dir}")
    print(f"Output directory: {combined_dir}")
    
    # Check if the data directory exists
    if not os.path.exists(data_dir):
        print(f"WARNING: Data directory not found at {data_dir}")
        print("Please update the script with the correct path to your data directory.")
        print("Your current directory structure based on error message:")
        print("- Project 2")
        print("  |- data-analysis-mapreduce")
        print("  |  |- combine_data.py")
        print("  |- data")
        print("     |- 2024")
        print("     |- 2025")
        exit(1)
        
    # Run the combination functions
    print("\n1. Combining CSV files by year...")
    combine_csv_by_year(data_dir, combined_dir)
    
    print("\n2. Creating master combined file...")
    combine_all_years(data_dir, combined_dir)
    
    print("\nProcess completed!")