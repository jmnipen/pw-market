import entsoe
import matplotlib.pylab as plt 
import pandas as pd 

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