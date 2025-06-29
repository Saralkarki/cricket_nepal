import pandas as pd
from pathlib import Path
from exploring_json_data_struct import extract_match_data
PROJECT_ROOT = Path(__file__).parent.parent
CODE_DIR = PROJECT_ROOT / 'code'
DATA_DIR = PROJECT_ROOT / 'data'

sample_json = f"{DATA_DIR}/Nepal/ODI/1154649.json"

match = extract_match_data(sample_json)
x_1 = match.convert_json_to_df(0)
x_2 = match.convert_json_to_df(1)

print(f"{x_1['runs.total'].sum()}/ {x_1['is_wicket'].sum()} ")
print(f"{x_2['runs.total'].sum()}/ {x_2['is_wicket'].sum()} ")


runs_compare = (x_1['runs.total'].sum()) - (x_2['runs.total'].sum())

if (runs_compare > 0):
    print(f"1st innings wins by {runs_compare} runs")
else:
    print("2nd innings wins by  wickets")

