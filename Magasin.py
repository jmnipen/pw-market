from DataExtractor import DataExtractor

import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import logger
import datetime

import os 

class Magasin():
    #Constructor
    def __init__(self, filter_omrType: list = None) -> None:
        self.price_zones: list = None
        
        self.magasin_data_path = './db/01_magasin_data.csv'
        
        self.magasin_data = self.load_magasin_data_from_db()
    
    
    #   
    def calc_stats_magasin_levels(self, 
                                  input_df: pd.DataFrame, 
                                  start_year: int, 
                                  end_year: int ) -> pd.DataFrame:
        input_df = input_df[input_df['iso_aar'].between(start_year, end_year)]
        
        stats_df = (
            input_df.groupby(["omrnr",  "iso_uke"])["fyllingsgrad"]
            .agg(min_fyllingsgrad="min", max_fyllingsgrad="max", mean_fyllingsgrad="mean")
            .reset_index()
        )
        
        # Create a copy of stats_df for each unique year in the input DataFrame
        all_years = input_df['iso_aar'].unique()  # Get unique years
        expanded_stats = []
        
        for year in all_years:
            temp_df = stats_df.copy()  # Copy the grouped stats
            temp_df['iso_aar'] = year  # Add the year column
            expanded_stats.append(temp_df)  # Append to the list
        # Combine all the yearly copies into a single DataFrame
        stats_df = pd.concat(expanded_stats, ignore_index=True)

        stats_df = stats_df[stats_df['iso_uke']<53]
        return stats_df
        
                
          
    def import_magasin_data(self) -> pd.DataFrame:
        data_extractor = DataExtractor()
        magasin = data_extractor.get_magasin_dataframe(['EL'])
        return magasin 
    
    def load_magasin_data_from_db(self) -> pd.DataFrame:
        """Load magasin data from the local CSV database."""
        magasin_df: pd.DataFrame = pd.read_csv(self.magasin_data_path, sep=';')
        
        return magasin_df
    
    def plot_magasin_data(self, start_year = 2020, end_year = 2025) -> None:
       
        #Filter only necessary columns
        magasin_df = self.magasin_data[['dato_Id', 'omrType', 'omrnr', 'iso_aar', 'iso_uke', 'fyllingsgrad', 'kapasitet_TWh', 'fylling_TWh']]     
        
        magasin_df = magasin_df[magasin_df['dato_Id'] > '2020-01-01']
        
        # Convert 'dato_Id' to datetime
        magasin_df['dato_Id'] = pd.to_datetime(magasin_df['dato_Id'])

        
        print(magasin_df)
        
        plt.figure(figsize=(12, 6  ))
        for omrnr, group in magasin_df.groupby('omrnr'):
            if omrnr == 2:
                plt.plot(group['dato_Id'], group['fyllingsgrad']*100, label=f'NO{omrnr}')
        
        # overlay weekly averages (min/max/mean) mapped to a reference year
        stats_df = self.calc_stats_magasin_levels(self.magasin_data, 2000, 2025)

        # detect which omrnr were actually plotted (labels like 'NO2')
        ax = plt.gca()
        plotted_omrns = []
        for line in ax.get_lines():
            lab = line.get_label()
            if isinstance(lab, str) and lab.startswith("NO"):
                try:
                    plotted_omrns.append(int(lab[2:]))
                except ValueError:
                    pass
        
        cmap = plt.get_cmap("tab10")
        for i, (omrnr, g) in enumerate(stats_df.groupby("omrnr")):
            if omrnr not in plotted_omrns:
                continue
            g = g.sort_values(["iso_aar", "iso_uke"])  # Sort by year and week
            weeks = g["iso_uke"].astype(int)
            years = g["iso_aar"].astype(int)  # Use the actual year from the data
            # Generate dates using both year and week
            dates = [pd.to_datetime(datetime.date.fromisocalendar(year, week, 1)) for year, week in zip(years, weeks)]
            ymin = g["min_fyllingsgrad"] * 100
            ymax = g["max_fyllingsgrad"] * 100
            mean = g["mean_fyllingsgrad"] * 100
            color = cmap(i % cmap.N)
            plt.fill_between(dates, ymin, ymax, color=color, alpha=0.25)
            plt.plot(dates, mean, color=color, label=f"NO{omrnr} mean", linestyle="--")    
                
        
        
        # Set x-axis major and minor ticks
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.YearLocator())  # Major ticks every year
        ax.xaxis.set_minor_locator(mdates.MonthLocator([4, 7, 10]))  # Minor ticks for April, July, and October
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format major ticks as year
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b'))  # Format minor ticks as month

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        # Add labels, legend, and title
        plt.xlim(datetime.datetime(start_year, 1, 1), datetime.datetime(end_year, 12, 31))
        plt.xlabel("Date")
        plt.ylabel("Fyllingsgrad")
        plt.title("Fyllingsgrad Over Time by Omrnr")
        plt.legend()
        plt.grid(True)    
        
        # Adjust layout to prevent overlap
        plt.tight_layout()
        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45)
        print(group['dato_Id'])
        plt.show()
        return
    
    def plot_stats_magasin_levels(self) -> None:
        stats_df = self.calc_stats_magasin_levels(self.magasin_data)
        
        plt.figure(figsize=(10, 6))
        cmap = plt.get_cmap("tab10")
        for i, (omrnr, group) in enumerate(stats_df.groupby("omrnr")):
            g = group.sort_values("iso_uke")
            x = g["iso_uke"]
            ymin = g["min_fyllingsgrad"] * 100
            ymax = g["max_fyllingsgrad"] * 100
            mean = g["mean_fyllingsgrad"] * 100

            color = cmap(i % cmap.N)
            plt.fill_between(x, ymin, ymax, color=color, alpha=0.25)
            plt.plot(x, mean, color=color, label=f"NO{omrnr} mean")

        plt.xlabel("ISO uke")
        plt.ylabel("Fyllingsgrad (%)")
        plt.title("Min/Max Fyllingsgrad per Omrnr (filled area) with Mean")
        plt.xlim(stats_df["iso_uke"].min(), stats_df["iso_uke"].max())
        plt.xticks(range(int(stats_df["iso_uke"].min()), int(stats_df["iso_uke"].max()) + 1, 4), rotation=45)
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        print(stats_df)
        
if __name__ == "__main__":
    mag = Magasin()
    #magasin_df = mag.import_magasin_data()
    
    print(mag.magasin_data)
    stats_df = mag.calc_stats_magasin_levels(mag.magasin_data, 2000, 2025)
    print(stats_df)
    mag.plot_magasin_data()
    mag.plot_stats_magasin_levels()