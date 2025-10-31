import json
import ast
import pandas as pd

file_location = 'logs/ml-logger.log'
content_logs = []
try:
    with open(file_location) as file:
       for line in file:
           content_logs.append(line.strip())
except FileNotFoundError:
    print(f"Error: file {file_location} was not found")
except Exception as e:
    print(f"An error occurred: {e}")

for txt in content_logs:
    if txt.find('ml-logger') == -1:
        content_logs.remove(txt)

for want_txt in content_logs:
    select_txt = want_txt.split(' | ')
    json_txt = json.loads((select_txt[1]))
    df = pd.DataFrame([json_txt["features"].values()], 
                        columns=json_txt["features"].keys())
    print(df.head())