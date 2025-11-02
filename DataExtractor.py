import requests # type: ignore
import pandas as pd # type: ignore
import os 
import logger # type: ignore

class DataExtractor:
    def __init__(self, filter_omrType: list = None) -> None:
        self.nve_magasin_data_url: str  = 'https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData'
        self.nve_magasin_data_url_last_week: str = 'https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligDataSisteUke'
        
        self.data_base_folder: str  = './db/'
        self.output_separator: str = ';' 
        
        self.filter_omrType = filter_omrType
        
        
    def update_hydrological_balance(self) -> None:
        """Update the hydrological balance of the system."""
        
        snow_level: float = 0.0 
        ground_water_level: float = 0 
        magasine_level: float = 0 
        
        
        
        ...        
        
    def calculate_runoff(self) -> float:
        
        """Calculate the runoff based on current conditions."""
        ...
        
    def parse_magasin_data(self)-> dict:
        """Fetch magasin data from NVE API."""
        
        headers: dict = {
            "accept": "application/json"
        }
        
        response: requests.Response = requests.get(self.nve_magasin_data_url, headers=headers)  
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the response to a file
            with open('Magasinstatistikk.json', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Response saved to Magasinstistikk.json")
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            
        self.response = response.json()
        
        return response.json()
    
    def parse_last_week_magasin_data(self) -> dict:

        # Request headers
        headers = {
            "accept": "application/json"
        }

        # Send GET request
        response = requests.get(self.nve_magasin_data_url_last_week, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the response to a file
            with open('Magasindstatistikk_siste_uke.json', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("Response saved to Magasindstatistikk_siste_uke.json")
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            
        self.response = response.json()
        
        return response.json()
    
    def get_last_week_magasin_dataframe(self) -> pd.DataFrame:
        """Convert last week's magasin data to a pandas DataFrame."""
        
        magasin_data_dict : dict = self.parse_last_week_magasin_data()
        
        for key in ('data', 'items', 'result', 'magasiner', 'Magasinstatistikk'):
            if key in magasin_data_dict and isinstance(magasin_data_dict[key], list):
                magasin_data_dict = magasin_data_dict[key]
                break
        
        if self.filter_omrType:
            magasin_data = [m for m in magasin_data_dict if m.get('omrType') in self.filter_omrType]
        else:
            magasin_data = list(magasin_data_dict)
        
        magasin_data = sorted(magasin_data, key=lambda x: (x["iso_aar"], x["iso_uke"]))
        
        return magasin_data
    
    def get_magasin_dataframe(self) -> pd.DataFrame:
        """Convert magasin data to a pandas DataFrame."""
        
        magasin_data_dict : dict = self.parse_magasin_data()
        
        # magasin_data_dict is JSON (likely a list of dicts). Normalize to a list first.
        for key in ('data', 'items', 'result', 'magasiner', 'Magasinstatistikk'):
            if key in magasin_data_dict and isinstance(magasin_data_dict[key], list):
                magasin_data_dict = magasin_data_dict[key]
                break

        if self.filter_omrType:
            magasin_data = [m for m in magasin_data_dict if m.get('omrType') in self.filter_omrType]
        else:
            magasin_data = list(magasin_data_dict)
        
        magasin_data = sorted(magasin_data, key=lambda x: (x["iso_aar"], x["iso_uke"]))   
    
        magasin_df: pd.DataFrame = pd.DataFrame(magasin_data)
             
        return magasin_df
    
    def save_magasin_dataframe(self, magasin_data_df: pd.DataFrame, filename: str = '01_magasin_data.csv') -> None:
        """Save the magasin DataFrame to a CSV file."""
        magasin_data_df.to_csv(os.path.join(self.data_base_folder, filename), index=False, sep = self.output_separator)
        print(f"Magasin data saved to {filename}")
        return
        
    def magasin_pipeline(self) -> None:
        
        magasin_data_df = self.get_magasin_dataframe()
        self.save_magasin_dataframe(magasin_data_df, filename='01_magasin_data.csv')
        
        return
    
    def update_magasin_pipeline(self) -> None:
        
        cur_magasin_data_df = self.get_last_week_magasin_dataframe()
        print(cur_magasin_data_df)
        with open(os.path.join(self.data_base_folder, '01_magasin_data.csv'), encoding='utf-8') as f:
            existing_df = pd.read_csv(f, sep=self.output_separator, encoding='utf-8')

            if not isinstance(cur_magasin_data_df, pd.DataFrame):
                cur_magasin_data_df = pd.DataFrame(cur_magasin_data_df)

            # Align columns so concat doesn't lose columns present in only one DF
            all_cols = list(dict.fromkeys(existing_df.columns.tolist() + cur_magasin_data_df.columns.tolist()))
            existing_df = existing_df.reindex(columns=all_cols)
            cur_magasin_data_df = cur_magasin_data_df.reindex(columns=all_cols)

            combined_df = pd.concat([existing_df, cur_magasin_data_df], ignore_index=True, sort=False)

            # Drop exact duplicate rows and sort if possible
            combined_df.drop_duplicates(inplace=True)
            if {'iso_aar', 'iso_uke'}.issubset(combined_df.columns):
                combined_df.sort_values(by=['iso_aar', 'iso_uke'], inplace=True)

            combined_df.to_csv(os.path.join(self.data_base_folder, '01_magasin_data_up.csv'),
                               index=False, sep=self.output_separator, encoding='utf-8')
            print("01_magasin_data-up.csv updated with last-week magasin data")
        
        return

if __name__ == "__main__":
    hyd = DataExtractor(filter_omrType=['EL'])
    hyd.magasin_pipeline()
    

