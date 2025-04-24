import pandas as pd

df = pd.read_csv("data\seasonal_temperatures.csv")

print(df.head())
print(df.columns)

# Create a pivot table with seasons as columns
pivoted_df = df.pivot_table(
    index=['StationID', 'Year'],
    columns='Season',
    values=['AverageTemp', 'MaxTemp', 'MinTemp']
)

# Flatten the column multi-index
pivoted_df.columns = [f'{val}_{season}' for val, season in pivoted_df.columns]

# Reset the index to make StationID and Year regular columns
pivoted_df = pivoted_df.reset_index()

pivoted_df = pivoted_df.interpolate()

# Calculate average for each season column across all stations
season_avgs = pivoted_df.mean()
season_avgs = round(season_avgs, 2)
pivoted_df = pivoted_df.fillna(season_avgs)
# Display the result
print(pivoted_df.head())

pivoted_df.to_csv('processed_data.csv', index=False)