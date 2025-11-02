from DataExtractor import DataExtractor

import pandas as pd 

class Magasin():
    
    def __init__(self):
        self.price_zones: list = None
        
    def import_magasin_data(self) -> pd.DataFrame:
        data_extractor = DataExtractor()
        magasin = data_extractor.get_magasin_dataframe()
        return magasin 
    
    def load_magasin_data_from_db(self) -> pd.DataFrame:
        """Load magasin data from the local CSV database."""
        magasin_df: pd.DataFrame = pd.read_csv('./db/01_magasin_data.csv', sep=';')
        return magasin_df
        