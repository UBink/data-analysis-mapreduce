# Data Analysis with MapReduce (Hadoop Streaming + Python)

This project performs large-scale temperature data analysis using **Hadoop MapReduce with Python scripts**. The goal is to extract seasonal insights and generate visualizations from multi-year climate sensor data.

## 📁 Project Structure

. ├── combine_data.py # Combines CSVs extracted from .tar.gz files ├── csv saver.py # Converts Hadoop output into a clean CSV ├── mapper.py # Mapper script for Hadoop Streaming job ├── reducer.py # Reducer script for Hadoop Streaming job ├── process.py # Post-MapReduce: cleans, structures data by year/season ├── visualization.py # Plots seasonal temperature trends ├── data/ │ ├── *.tar.gz (ignored, can be downloaded from https://www.ncei.noaa.gov/data/global-summary-of-the-day/archive/) # Raw yearly climate data archives │ ├── seasonal_temperatures.csv # Output from MapReduce (season stats) │ └── processed_data.csv # Final cleaned data, structured by year/season


## 🔁 Workflow Overview

1. **Data Preparation**  
   - Place raw `.tar.gz` files for each year into `data/`  
   - Use `combine_data.py` to extract and merge into a base CSV

2. **MapReduce Job (Hadoop Streaming)**  
   - `mapper.py`: emits key-value pairs (e.g. `(season, temp)`)  
   - `reducer.py`: computes stats like min, max, or average per season

   Example command:
   ```bash
   hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
     -input /data/combined_data.csv \
     -output /output/seasonal_analysis \
     -mapper /mnt/c/hadoop/hadoop-3.4.1/scripts/mapper.py \
     -reducer /mnt/c/hadoop/hadoop-3.4.1/scripts/reducer.py

**3. Post-Processing**

Run csv saver.py to extract Hadoop output into a CSV

Run process.py to organize it by year and season → processed_data.csv

**4. Visualization**

Use visualization.py to plot trends across years/seasons
