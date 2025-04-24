import os
import pandas as pd
import tarfile
import io
import glob
import re

def find_data_directory():
    """
    Automatically find the data directory containing year folders or tar files.
    Looks for patterns like directories named '2024', '2025', or files with .tar extension.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    # Places to look for data, in order of priority
    locations_to_check = [
        script_dir,                                
        os.path.join(script_dir, 'data'),          
        os.path.dirname(script_dir),               
        os.path.join(os.path.dirname(script_dir), 'data')  
    ]
    
    # What to look for to identify data directory
    def is_data_directory(path):
        if not os.path.exists(path):
            return False
            
        # Look for year folders
        if any(os.path.isdir(os.path.join(path, str(year))) for year in range(2020, 2026)):
            return True
            
        # Look for tar files
        if any(f.endswith('.tar') or f.endswith('.tar.gz') for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))):
            return True
            
        # Look for csv files
        if any(f.endswith('.csv') for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))):
            return True
            
        return False
    
    # Check each location
    for location in locations_to_check:
        if is_data_directory(location):
            print(f"Found data directory: {location}")
            return location
    
    # If it gets here, couldn't find the data directory
    print("Could not automatically find data directory.")
    
    # Last resort: search recursively up to 2 levels down from script directory
    print("Searching recursively for data directory...")
    for root, dirs, files in os.walk(script_dir, topdown=True):
        if root.count(os.sep) - script_dir.count(os.sep) > 2:
            # Don't go deeper than 2 levels
            continue
        
        if is_data_directory(root):
            print(f"Found data directory: {root}")
            return root
            
    return None

def combine_csv_from_tar_by_year(tar_dir, output_dir):
 
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Get all tar files
    tar_files = glob.glob(os.path.join(tar_dir, "*.tar"))
    tar_files += glob.glob(os.path.join(tar_dir, "*.tar.gz"))
    
    if not tar_files:
        print(f"No tar files found in {tar_dir}")
        return None
    
    print(f"Found {len(tar_files)} tar archives")
    
    # Dictionary to hold df by year
    year_data = {}
    total_files_processed = 0
    
    # Process each tar file
    for tar_path in tar_files:
        tar_name = os.path.basename(tar_path)
        print(f"Processing archive: {tar_name}")
        
        try:
            with tarfile.open(tar_path, 'r:*') as tar:
                # Get all csv files from the archive
                csv_files = [f for f in tar.getnames() if f.lower().endswith('.csv')]
                
                if not csv_files:
                    print(f"  No CSV files found in {tar_name}. Skipping.")
                    continue
                
                print(f"  Found {len(csv_files)} CSV files in archive")
                archive_files_processed = 0
                
                # Process each csv file in the tar archive
                for csv_file in csv_files:
                    try:
                        # Extract year from the file path
                        path_parts = csv_file.split('/')
                        year = None
                        
                        # Look for year in path parts
                        for part in path_parts:
                            if part.isdigit() and len(part) == 4:
                                year = part
                                break
                        
                        # If no year found in path, try to extract from filename
                        if not year:
                            filename = os.path.basename(csv_file)
                            # Look for 4-digit year in filename
                            year_match = re.search(r'(19|20)\d{2}', filename)
                            if year_match:
                                year = year_match.group(0)
                        
                        # If still no year, use the tar filename
                        if not year:
                            year_match = re.search(r'(19|20)\d{2}', tar_name)
                            if year_match:
                                year = year_match.group(0)
                            else:
                                year = "unknown"
                        
                        # Extract file from tar and read as df
                        file_obj = tar.extractfile(csv_file)
                        if file_obj:
                            content = file_obj.read()
                            df = pd.read_csv(io.BytesIO(content))
                            
                            # Add to the year's df
                            if year not in year_data:
                                year_data[year] = []
                            
                            year_data[year].append(df)
                            
                            # Update counters
                            archive_files_processed += 1
                            total_files_processed += 1
                            
                            # Notify every 1000 files
                            if total_files_processed % 1000 == 0:
                                print(f"    Progress: Processed {total_files_processed} files total")
                        else:
                            print(f"    Error: Could not extract {csv_file}")
                    
                    except Exception as e:
                        print(f"    Error processing {csv_file}: {e}")
                
                print(f"  Completed processing {archive_files_processed} files from {tar_name}")
        
        except Exception as e:
            print(f"  Error opening tar file {tar_name}: {e}")
    
    print(f"Total files processed across all archives: {total_files_processed}")
    
    # Combine and save data for each year
    for year, dfs in year_data.items():
        if not dfs:
            print(f"No valid data found for {year}")
            continue
        
        print(f"Combining {len(dfs)} files for year {year}...")
        
        # Combine all dfs for this year
        combined_df = pd.concat(dfs, ignore_index=True)
        
        if not combined_df.empty:
            output_file = os.path.join(output_dir, f"{year}_combined.csv")
            combined_df.to_csv(output_file, index=False)
            print(f"Saved combined data for {year} to {output_file}")
            print(f"  Total rows: {len(combined_df)}")
    
    return year_data.keys() if year_data else None

def combine_csv_by_year(data_dir, output_dir):
  
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Check if there are year directories
    potential_year_dirs = [d for d in os.listdir(data_dir) 
                         if os.path.isdir(os.path.join(data_dir, d)) and 
                         (d.isdigit() or re.match(r'(19|20)\d{2}', d))]
    
    if not potential_year_dirs:
        print(f"No year directories found in {data_dir}")
        return None
    
    print(f"Found year directories: {potential_year_dirs}")
    years_processed = []
    
    for year_dir in potential_year_dirs:
        year_path = os.path.join(data_dir, year_dir)
        csv_files = glob.glob(os.path.join(year_path, '*.csv'))
        
        if not csv_files:
            print(f"No CSV files found in {year_path}. Skipping.")
            continue
        
        print(f"Processing {len(csv_files)} CSV files from {year_dir}...")
        
        # Initialize an empty dfs to hold combined data
        combined_data = pd.DataFrame()
        files_processed = 0
        
        # Read and combine all csv files for the current year
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                combined_data = pd.concat([combined_data, df], ignore_index=True)
                files_processed += 1
                
                # Notify every 1000 files
                if files_processed % 1000 == 0:
                    print(f"  Progress: Processed {files_processed} files")
                
            except Exception as e:
                print(f"  Error processing {os.path.basename(file)}: {e}")
        
        if not combined_data.empty:
            # Save the combined data
            output_file = os.path.join(output_dir, f"{year_dir}_combined.csv")
            combined_data.to_csv(output_file, index=False)
            print(f"Saved combined data for {year_dir} to {output_file}")
            print(f"  Total rows: {len(combined_data)}")
            years_processed.append(year_dir)
        else:
            print(f"No valid data found for {year_dir}")
    
    return years_processed

def combine_all_years(output_dir, years=None):
    
    if years is None or not years:
        # Get all combined files if years not provided
        combined_files = glob.glob(os.path.join(output_dir, '*_combined.csv'))
    else:
        combined_files = [os.path.join(output_dir, f"{year}_combined.csv") for year in years]
        # Filter to only files that exist
        combined_files = [f for f in combined_files if os.path.exists(f)]
    
    if not combined_files:
        print("No combined files found to merge.")
        return
    
    print(f"\nCombining all {len(combined_files)} year files into one master file...")
    
    # Initialize an empty df to hold combined data
    all_data = pd.DataFrame()
    files_processed = 0
    
    # Read and combine all year files
    for file in combined_files:
        try:
            df = pd.read_csv(file)
            all_data = pd.concat([all_data, df], ignore_index=True)
            files_processed += 1
            print(f"  Added: {os.path.basename(file)}")
        except Exception as e:
            print(f"  Error processing {os.path.basename(file)}: {e}")
    
    if not all_data.empty:
        # Save the master combined data
        output_file = os.path.join(output_dir, "all_years_combined.csv")
        all_data.to_csv(output_file, index=False)
        print(f"Saved master combined data to {output_file}")
        print(f"  Total files combined: {files_processed}")
        print(f"  Total rows: {len(all_data)}")
    else:
        print("No valid data found to combine.")

if __name__ == "__main__":
    print("Data Combiner - Auto-detecting directories...")
    
    # Auto-detect data directory
    data_dir = find_data_directory()
    
    if not data_dir:
        print("Could not find data directory automatically.")
        data_dir = input("Please enter the path to your data directory: ")
    
    # Get the script directory for output
    script_dir = os.path.dirname(os.path.abspath(__file__))
    combined_dir = os.path.join(script_dir, 'combined_data')
    
    print(f"\nData directory: {data_dir}")
    print(f"Output directory: {combined_dir}")
    
    # Determine if we should process tar files or regular csv files
    tar_files = glob.glob(os.path.join(data_dir, "*.tar")) + glob.glob(os.path.join(data_dir, "*.tar.gz"))
    
    years = None
    
    if tar_files:
        print("\n1. Found tar files - Combining CSV files from tar archives by year...")
        years = combine_csv_from_tar_by_year(data_dir, combined_dir)
    else:
        print("\n1. No tar files found - Looking for year directories with CSV files...")
        years = combine_csv_by_year(data_dir, combined_dir)
    
    if years:
        print("\n2. Creating master combined file...")
        combine_all_years(combined_dir, years)
        print("\nProcess completed successfully!")
    else:
        print("\nNo data was processed. Please check your directory structure.")