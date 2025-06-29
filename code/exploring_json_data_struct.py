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
            # print(i+1,over_struct)
            # print(type(over_struct))
    
    def convert_json_to_df(self, innings=0):
        """Convert the JSON data to a DataFrame"""
        
        # flatten the overs and deliveries
        all_deliveries = []
        inns_overs = self.data['innings'][innings]['overs']
        
        for over_num, over in enumerate(inns_overs):
            for delivery_num, delivery in enumerate(over['deliveries']):
                # Add over and ball information as separate columns
                delivery['overs'] = over_num + 1  # +1 for 1-based indexing
                delivery['balls'] = delivery_num + 1  # +1 for 1-based indexing
                all_deliveries.append(delivery)
                
        innings_1_df = pd.json_normalize(all_deliveries)

        # Add empty columns for future use
        innings_1_df['description'] = ""
        innings_1_df['ball_areas'] = ""
        innings_1_df['is_wicket'] = ""
        innings_1_df['is_drs'] = ""
        innings_1_df['is_umpires_call'] = ""

        # flatten wickets column - handle NaN values (only if wickets column exists)
        if 'wickets' in innings_1_df.columns:
            innings_1_df['wicket_player_out'] = innings_1_df['wickets'].apply(lambda x: x[0]['player_out'] if isinstance(x, list) and len(x) > 0 else None)
            innings_1_df['wicket_kind'] = innings_1_df['wickets'].apply(lambda x: x[0]['kind'] if isinstance(x, list) and len(x) > 0 else None)
            innings_1_df['wicket_fielder'] = innings_1_df['wickets'].apply(lambda x: x[0]['fielders'][0]['name'] if isinstance(x, list) and len(x) > 0 and 'fielders' in x[0] and x[0]['fielders'] else None)
            # Drop the original wickets column
            innings_1_df.drop('wickets', axis=1, inplace=True)
        
        # Create missing extras columns if they don't exist
        extras_columns = ['extras.wides', 'extras.legbyes', 'extras.noballs', 'extras.byes']
        for col in extras_columns:
            if col not in innings_1_df.columns:
                innings_1_df[col] = None
        
        # Create missing runs columns if they don't exist
        runs_columns = ['runs.batter', 'runs.extras', 'runs.total']
        for col in runs_columns:
            if col not in innings_1_df.columns:
                innings_1_df[col] = 0  # Default to 0 for runs
        
        # Create missing wicket columns if they don't exist
        wicket_columns = ['wicket_player_out', 'wicket_kind', 'wicket_fielder']
        for col in wicket_columns:
            if col not in innings_1_df.columns:
                innings_1_df[col] = None
        
        # Arrange columns in the specified order
        base_columns = ['overs', 'balls', 'batter', 'non_striker', 'bowler','runs.batter',  'description',
                        'runs.extras', 'runs.total',
                         'extras.wides','extras.legbyes','extras.noballs','ball_areas', 'is_wicket',
                         'wicket_player_out', 'wicket_kind',
                         'wicket_fielder','is_drs', 'is_umpires_call']
        
        # Only include columns that actually exist in the dataframe
        existing_columns = [col for col in base_columns if col in innings_1_df.columns]
        
        # Reorder the DataFrame columns
        innings_1_df = innings_1_df[existing_columns]
        
        # Populate is_wicket column based on wicket_player_out
        innings_1_df = self.populate_wicket_flag(innings_1_df)
        
        return innings_1_df
    
    def populate_wicket_flag(self, df):
        """Populate is_wicket column based on wicket_player_out"""
        # Using pandas methods - more efficient than lambda
        df['is_wicket'] = df['wicket_player_out'].notna().astype(int)
        return df
    
match = extract_match_data(sample_json)
print('done')
# x = match.convert_json_to_df(1)
# print(x.head())

# x = match.get_match_info()
# print(x.head())

# match.convert_json_to_df(1).to_excel(f"{DATA_DIR}/test/test.xlsx", index=False)
