import pandas as pd
import json
from pathlib import Path
import os


'''
Looking the json data struture,
- The top-level structure is a dictionary.
- Meta, Info and Innings are the main keys.
- The 'info' key contains metadata about the match.
- The 'innings' key contains a list of innings, each with its own structure.
- Each innings has a 'team' key indicating the team name.
- The first team [0] is the batting team, and the second team [1] is the bowling team.
-

'''

PROJECT_ROOT = Path(__file__).parent.parent
CODE_DIR = PROJECT_ROOT / 'code'
DATA_DIR = PROJECT_ROOT / 'data'

sample_json = f"{DATA_DIR}/Nepal/ODI/1154649.json"


''' Use case
match = extract_match_data(sample_json)

# Now call the method on the instance
match_info = match.get_match_info()
print(match_info)
'''

# Create an instance of the class

class extract_match_data:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = self.load_data()
    
    def load_data(self):
        with open(self.json_file_path, 'r') as f:
            return json.load(f)
    
    def get_match_info(self):
        """Extract match information and return as DataFrame"""
        info = self.data['info']
        df = pd.json_normalize(info, max_level=1)
        return df
    
    def test_data_structure(self, over):
        """Test the structure of the overs"""
        inns_1 = self.data['innings'][0]
        inns_overs = inns_1['overs']
        for i in range(len(inns_1['overs'][over]['deliveries'])):
            over_struct = inns_1['overs'][over]['deliveries'][i]
            print(i+1,over_struct)
            print(type(over_struct))
    
    def convert_json_to_df(self, innings=0):
        """Convert the JSON data to a DataFrame"""
        
#  flatten the overs and deliveries
        all_deliveries = []
        inns_overs = self.data['innings'][innings]['overs']
        for over in inns_overs:
            all_deliveries.extend(over['deliveries'])
            
        innings_1_df = pd.json_normalize(all_deliveries, max_level=1)

        #  flatten wickets column - handle NaN values
        innings_1_df['wicket_player_out'] = innings_1_df['wickets'].apply(lambda x: x[0]['player_out'] if isinstance(x, list) and len(x) > 0 else None)
        innings_1_df['wicket_kind'] = innings_1_df['wickets'].apply(lambda x: x[0]['kind'] if isinstance(x, list) and len(x) > 0 else None)
        innings_1_df['wicket_fielder'] = innings_1_df['wickets'].apply(lambda x: x[0]['fielders'][0]['name'] if isinstance(x, list) and len(x) > 0 and 'fielders' in x[0] and x[0]['fielders'] else None)

        # Drop the original wickets column if you want
        innings_1_df.drop('wickets', axis=1, inplace=True)
        return innings_1_df

match = extract_match_data(sample_json)

# x = match.convert_json_to_df(1)
# print(x.head())

print(type(match.get_match_info()))
x = match.get_match_info()
print(x.head())
x.to_csv(f"{DATA_DIR}/test/test_info.csv", index=False)
