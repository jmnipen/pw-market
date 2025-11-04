import entsoe # type :ignore
import matplotlib.pyplot  as plt # type :ignore
import pandas as pd # type :ignore

class EntsoeClient:
    """
    
    
    Base class for interacting with the ENTSO-E API.
    """
    def __init__(self, api_key):
        self.client = entsoe.EntsoePandasClient(api_key=api_key)
    
    def query_data(self, start_date, end_date, biddingzones, query_function):
        """
        Generic method to query data from ENTSO-E API.
        """
        start = pd.Timestamp(start_date, tz='Europe/Brussels')
        end = pd.Timestamp(end_date, tz='Europe/Brussels')
        data = {}
        
        for zone in biddingzones:
            data[zone] = query_function(zone, start, end)
        
        df = pd.concat(data, axis=1)
        df.columns = biddingzones
        return df
    
    
class PriceData(EntsoeClient):
    """
    Class for fetching and processing day-ahead price data.
    """
    def __init__(self, api_key):
        super().__init__(api_key)
    
    def get_day_ahead_prices(self, start_date, end_date, biddingzones):
        """
        Fetch day-ahead prices for given bidding zones and time range.
        """
        return self.query_data(start_date, end_date, biddingzones, self.client.query_day_ahead_prices)
    
class ProductionData(EntsoeClient):
    """
    Class for fetching and processing production data.
    """
    def __init__(self, api_key):
        super().__init__(api_key)
    
    def get_production_data(self, start_date, end_date, biddingzones):
        """
        Fetch production data for given bidding zones and time range.
        """
        return self.query_data(start_date, end_date, biddingzones, self.client.query_generation)
    
class Illustrate:
    """
    Class for plotting different types of data.
    """
    def __init__(self, df, title="Data Visualization", xlabel="Time", ylabel="Value"):
        self.df = df
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

    def plot(self):
        """
        Plots the dataframe.
        """
        plt.figure(figsize=(12, 6))
        for column in self.df.columns:
            plt.plot(self.df.index, self.df[column], label=column)

        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend()
        plt.grid(True)
        plt.show()
        

if __name__ == "__main__":
    API_KEY = "c451871d-ac6a-4242-ac3e-8c7e5530dbab"
    
    # Initialize client
    client = PriceData(API_KEY)

    # Define parameters
    start_date = "2024-03-01"
    end_date = "2024-03-10"
    biddingzones = ["DE_LU", "FR"]  # Example bidding zones

    # Fetch price data
    df_prices = client.get_day_ahead_prices(start_date, end_date, biddingzones)

    # Plot the data
    if not df_prices.empty:
        plotter = Illustrate(df_prices, title="Day-Ahead Prices", ylabel="€/MWh")
        plotter.plot()
    else:
        print("No data available for plotting.")
        
        
