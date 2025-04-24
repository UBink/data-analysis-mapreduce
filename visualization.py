import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the data
filled_df = pd.read_csv('data\processed_data.csv')

# Define the seasons and other constants
seasons = ['Winter', 'Spring', 'Summer', 'Fall']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Different color for each season
stations = filled_df['StationID'].unique()
years = filled_df['Year'].unique()

# Seasonal Temperature Comparison
fig, axes = plt.subplots(3, 1, figsize=(12, 15))
titles = ['Average Temperature', 'Maximum Temperature', 'Minimum Temperature']
metrics = ['AverageTemp', 'MaxTemp', 'MinTemp']

for i, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[i]
    
    # Collect data for each season
    for j, season in enumerate(seasons):
        col_name = f'{metric}_{season}'
        if col_name in filled_df.columns:
            data = filled_df[col_name].dropna()
            
            # Create box plot manually
            bp = ax.boxplot(data, positions=[j+1], widths=0.6, patch_artist=True)
            
            # Set box color
            for box in bp['boxes']:
                box.set(color=colors[j], linewidth=2)
                box.set(facecolor=colors[j], alpha=0.3)
            
            # Set whisker color
            for whisker in bp['whiskers']:
                whisker.set(color=colors[j], linewidth=2)
            
            # Set cap color
            for cap in bp['caps']:
                cap.set(color=colors[j], linewidth=2)
            
            # Set median color
            for median in bp['medians']:
                median.set(color='black', linewidth=2)
    
    ax.set_title(f'{title} by Season (All Stations)')
    ax.set_ylabel('Temperature (°F)')
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(seasons)
    ax.grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('seasonal_temperatures.png', dpi=300)
plt.show()

# Year-over-Year Trends - Select top 8 stations to avoid overcrowding
plt.figure(figsize=(12, 8))

# Sort stations by average summer temperature to pick meaningful subset
if 'AverageTemp_Summer' in filled_df.columns:
    station_avg_temp = []
    for station in stations:
        avg = filled_df[filled_df['StationID'] == station]['AverageTemp_Summer'].mean()
        station_avg_temp.append((station, avg))
    
    # Sort by temperature and take top 8
    station_avg_temp.sort(key=lambda x: x[1] if not np.isnan(x[1]) else -999, reverse=True)
    selected_stations = [x[0] for x in station_avg_temp[:8] if not np.isnan(x[1])]
else:
    # If no Summer data, just take first 8 stations
    selected_stations = stations[:8]

for station in selected_stations:
    station_data = filled_df[filled_df['StationID'] == station]
    if 'AverageTemp_Summer' in filled_df.columns:
        plt.plot(station_data['Year'], station_data['AverageTemp_Summer'], 
                marker='o', linewidth=2, label=f'Station {station}')

plt.title('Summer Average Temperature Trends by Station (Top 8 Stations)')
plt.xlabel('Year')
plt.ylabel('Temperature (°F)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('yearly_trends_fixed.png', dpi=300)
plt.show()

# Heatmap of temperature data - display only top 15 stations for readability
plt.figure(figsize=(12, 10))

# Select top 15 stations by data availability
if len(stations) > 15:
    station_counts = []
    for station in stations:
        if 'AverageTemp_Summer' in filled_df.columns:
            count = filled_df[filled_df['StationID'] == station]['AverageTemp_Summer'].notna().sum()
            station_counts.append((station, count))
    
    # Sort by data availability
    station_counts.sort(key=lambda x: x[1], reverse=True)
    display_stations = [x[0] for x in station_counts[:15]]
else:
    display_stations = stations

# Create a data matrix for the heatmap
heatmap_data = np.zeros((len(display_stations), len(years)))

for i, station in enumerate(display_stations):
    for j, year in enumerate(years):
        mask = (filled_df['StationID'] == station) & (filled_df['Year'] == year)
        if mask.any() and 'AverageTemp_Summer' in filled_df.columns:
            temp = filled_df.loc[mask, 'AverageTemp_Summer'].values
            if len(temp) > 0 and not np.isnan(temp[0]):
                heatmap_data[i, j] = temp[0]

im = plt.imshow(heatmap_data, cmap='YlOrRd')
plt.colorbar(im, label='Temperature (°F)')
plt.title('Summer Average Temperatures by Station and Year')
plt.xlabel('Year')
plt.ylabel('Station ID')

# Add x and y tick labels with better formatting
plt.xticks(range(len(years)), years, rotation=45)
plt.yticks(range(len(display_stations)), [str(s)[-4:] for s in display_stations])  # Show last 4 digits only

# Add annotations - only for non-zero values
for i in range(len(display_stations)):
    for j in range(len(years)):
        if heatmap_data[i, j] > 0:  # Only annotate non-zero values
            plt.text(j, i, f'{heatmap_data[i, j]:.1f}', 
                     ha='center', va='center', 
                     color='black' if heatmap_data[i, j] < 70 else 'white',
                     fontsize=8)

plt.tight_layout()
plt.savefig('temperature_heatmap_fixed.png', dpi=300)
plt.show()

# Bar chart showing seasonal averages by station limit to 10 stations for readability
plt.figure(figsize=(16, 8))
bar_width = 0.2

# Select top 10 stations with most complete data
if len(stations) > 10:
    data_counts = []
    for station in stations:
        count = 0
        for season in seasons:
            col_name = f'AverageTemp_{season}'
            if col_name in filled_df.columns:
                count += filled_df[filled_df['StationID'] == station][col_name].notna().sum()
        data_counts.append((station, count))
    
    # Sort by data completeness
    data_counts.sort(key=lambda x: x[1], reverse=True)
    display_stations = [x[0] for x in data_counts[:10]]
else:
    display_stations = stations

x = np.arange(len(display_stations))

for i, season in enumerate(seasons):
    col_name = f'AverageTemp_{season}'
    if col_name in filled_df.columns:
        season_avgs = [filled_df[filled_df['StationID'] == station][col_name].mean() 
                     for station in display_stations]
        plt.bar(x + i*bar_width, season_avgs, width=bar_width, 
                label=season, alpha=0.7)

plt.xlabel('Station ID')
plt.ylabel('Average Temperature (°F)')
plt.title('Average Temperature by Station and Season')
# Show shortened station IDs for readability
plt.xticks(x + bar_width*1.5, [str(s)[-4:] for s in display_stations], rotation=45)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('station_season_averages_fixed.png', dpi=300)
plt.show()

# Summary statistics table for the report
print("\nSummary Statistics by Season:")
for season in seasons:
    avg_col = f'AverageTemp_{season}'
    max_col = f'MaxTemp_{season}'
    min_col = f'MinTemp_{season}'
    
    if avg_col in filled_df.columns:
        avg_temp = filled_df[avg_col].mean()
        avg_std = filled_df[avg_col].std()
        
        max_temp = filled_df[max_col].mean() if max_col in filled_df.columns else np.nan
        min_temp = filled_df[min_col].mean() if min_col in filled_df.columns else np.nan
        
        station_count = filled_df[avg_col].notna().sum()
        
        print(f"\n{season}:")
        print(f"  Average Temperature: {avg_temp:.2f}°F (±{avg_std:.2f})")
        print(f"  Average Maximum: {max_temp:.2f}°F")
        print(f"  Average Minimum: {min_temp:.2f}°F")
        print(f"  Data points: {station_count}")

#  Average temperature over years for all stations
plt.figure(figsize=(12, 6))

yearly_avgs = {}
for season in seasons:
    col_name = f'AverageTemp_{season}'
    if col_name in filled_df.columns:
        yearly_avgs[season] = filled_df.groupby('Year')[col_name].mean()

for season, avgs in yearly_avgs.items():
    plt.plot(avgs.index, avgs.values, marker='o', linewidth=2, label=season)

plt.title('Average Temperature Trends by Season (All Stations)')
plt.xlabel('Year')
plt.ylabel('Temperature (°F)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('yearly_season_trends.png', dpi=300)
plt.show()