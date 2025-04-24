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
plt.savefig('seasonal_temperatures.png')
plt.show()

# Year-over-Year Trends
plt.figure(figsize=(12, 8))

for station in stations:
    station_data = filled_df[filled_df['StationID'] == station]
    if 'AverageTemp_Summer' in filled_df.columns:
        plt.plot(station_data['Year'], station_data['AverageTemp_Summer'], 
                marker='o', label=f'Station {station}')

plt.title('Summer Average Temperature Trends by Station')
plt.xlabel('Year')
plt.ylabel('Temperature (°F)')
plt.legend()
plt.grid(True)
plt.savefig('yearly_trends.png')
plt.show()


# Create a data matrix for the heatmap
heatmap_data = np.zeros((len(stations), len(years)))

for i, station in enumerate(stations):
    for j, year in enumerate(years):
        mask = (filled_df['StationID'] == station) & (filled_df['Year'] == year)
        if mask.any() and 'AverageTemp_Summer' in filled_df.columns:
            temp = filled_df.loc[mask, 'AverageTemp_Summer'].values
            if len(temp) > 0 and not np.isnan(temp[0]):
                heatmap_data[i, j] = temp[0]

plt.figure(figsize=(10, 8))
im = plt.imshow(heatmap_data, cmap='YlOrRd')
plt.colorbar(im, label='Temperature (°F)')
plt.title('Summer Average Temperatures by Station and Year')
plt.xlabel('Year')
plt.ylabel('Station ID')

# Add x and y tick labels
plt.xticks(range(len(years)), years)
plt.yticks(range(len(stations)), stations)

# Add annotations
for i in range(len(stations)):
    for j in range(len(years)):
        if heatmap_data[i, j] > 0:  # Only annotate non-zero values
            plt.text(j, i, f'{heatmap_data[i, j]:.1f}', 
                     ha='center', va='center', 
                     color='black' if heatmap_data[i, j] < 70 else 'white')

plt.tight_layout()
plt.savefig('temperature_heatmap.png')
plt.show()

# Bar chart for seasonal averages by station
plt.figure(figsize=(14, 8))
bar_width = 0.2
x = np.arange(len(stations))

for i, season in enumerate(seasons):
    col_name = f'AverageTemp_{season}'
    if col_name in filled_df.columns:
        season_avgs = [filled_df[filled_df['StationID'] == station][col_name].mean() 
                      for station in stations]
        plt.bar(x + i*bar_width, season_avgs, width=bar_width, 
                label=season, alpha=0.7)

plt.xlabel('Station ID')
plt.ylabel('Average Temperature (°F)')
plt.title('Average Temperature by Station and Season')
plt.xticks(x + bar_width*1.5, stations)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.3)
plt.savefig('station_season_averages.png')
plt.show()

# Summary 
print("\nSummary Statistics by Station:")
for station in stations:
    station_data = filled_df[filled_df['StationID'] == station]
    print(f"\nStation {station}:")
    
    for season in seasons:
        col_name = f'AverageTemp_{season}'
        if col_name in filled_df.columns:
            avg_temp = station_data[col_name].mean()
            max_temp = station_data[f'MaxTemp_{season}'].mean() if f'MaxTemp_{season}' in filled_df.columns else np.nan
            min_temp = station_data[f'MinTemp_{season}'].mean() if f'MinTemp_{season}' in filled_df.columns else np.nan
            
            print(f"  {season}: Avg={avg_temp:.2f}°F, Max={max_temp:.2f}°F, Min={min_temp:.2f}°F")